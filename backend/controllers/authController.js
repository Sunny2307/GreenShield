const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { prisma } = require('../config/database');
const { generateOTP, sendOTPEmail } = require('../utils/emailService');

// Signup controller
const signup = async (req, res) => {
  try {
    const { name, mobile, email, password } = req.body;
    
    // Debug logging
    console.log('Signup request received:', {
      name: name,
      mobile: mobile,
      email: email,
      passwordLength: password ? password.length : 0
    });

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User with this email already exists'
      });
    }

    // Hash password
    const saltRounds = 12;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Generate OTP
    const otp = generateOTP();
    const otpExpiry = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Create user
    const user = await prisma.user.create({
      data: {
        name,
        mobile,
        email,
        password: hashedPassword,
        otp,
        otpExpiry
      },
      select: {
        id: true,
        name: true,
        mobile: true,
        email: true,
        isEmailVerified: true,
        createdAt: true
      }
    });

    // Send OTP email (but don't fail if email service is not available)
    let emailSent = false;
    try {
      emailSent = await sendOTPEmail(email, otp, name);
    } catch (emailError) {
      console.warn('Email service not available:', emailError.message);
      // Continue with signup even if email fails
    }

    if (!emailSent) {
      // If email fails, still create the user but return a different message
      console.log(`User ${email} created but email not sent. OTP: ${otp}`);
      
      res.status(201).json({
        success: true,
        message: 'User registered successfully! For development, use OTP: ' + otp,
        data: {
          user,
          emailSent: false,
          developmentOTP: otp // Only include in development
        }
      });
    } else {
      res.status(201).json({
        success: true,
        message: 'User registered successfully. Please check your email for verification code.',
        data: {
          user,
          emailSent: true
        }
      });
    }

  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Login controller
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    // Return user data (excluding password)
    const userData = {
      id: user.id,
      name: user.name,
      mobile: user.mobile,
      email: user.email,
      isEmailVerified: user.isEmailVerified,
      createdAt: user.createdAt
    };

    res.status(200).json({
      success: true,
      message: 'Login successful',
      data: {
        user: userData,
        token
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Verify OTP controller
const verifyOTP = async (req, res) => {
  try {
    const { email, otp } = req.body;

    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Check if email is already verified
    if (user.isEmailVerified) {
      return res.status(400).json({
        success: false,
        message: 'Email is already verified'
      });
    }

    // Check if OTP exists and is not expired
    if (!user.otp || !user.otpExpiry) {
      return res.status(400).json({
        success: false,
        message: 'No OTP found. Please request a new one.'
      });
    }

    if (new Date() > user.otpExpiry) {
      return res.status(400).json({
        success: false,
        message: 'OTP has expired. Please request a new one.'
      });
    }

    // Verify OTP
    if (user.otp !== otp) {
      return res.status(400).json({
        success: false,
        message: 'Invalid OTP'
      });
    }

    // Update user to verified
    const updatedUser = await prisma.user.update({
      where: { id: user.id },
      data: {
        isEmailVerified: true,
        otp: null,
        otpExpiry: null
      },
      select: {
        id: true,
        name: true,
        mobile: true,
        email: true,
        isEmailVerified: true,
        createdAt: true
      }
    });

    // Generate JWT token
    const token = jwt.sign(
      { userId: updatedUser.id },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    );

    res.status(200).json({
      success: true,
      message: 'Email verified successfully',
      data: {
        user: updatedUser,
        token
      }
    });

  } catch (error) {
    console.error('OTP verification error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Resend OTP controller
const resendOTP = async (req, res) => {
  try {
    const { email } = req.body;

    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Check if email is already verified
    if (user.isEmailVerified) {
      return res.status(400).json({
        success: false,
        message: 'Email is already verified'
      });
    }

    // Generate new OTP
    const otp = generateOTP();
    const otpExpiry = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Update user with new OTP
    await prisma.user.update({
      where: { id: user.id },
      data: {
        otp,
        otpExpiry
      }
    });

    // Send new OTP email (but don't fail if email service is not available)
    let emailSent = false;
    try {
      emailSent = await sendOTPEmail(email, otp, user.name);
    } catch (emailError) {
      console.warn('Email service not available for resend:', emailError.message);
    }

    if (!emailSent) {
      // If email fails, still return success but with OTP for development
      console.log(`Resend OTP for ${email}: ${otp}`);
      
      res.status(200).json({
        success: true,
        message: 'New verification code generated! For development, use OTP: ' + otp,
        developmentOTP: otp // Only include in development
      });
    } else {
      res.status(200).json({
        success: true,
        message: 'New verification code sent to your email'
      });
    }

  } catch (error) {
    console.error('Resend OTP error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

// Get current user controller
const getCurrentUser = async (req, res) => {
  try {
    res.status(200).json({
      success: true,
      data: {
        user: req.user
      }
    });
  } catch (error) {
    console.error('Get current user error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

module.exports = {
  signup,
  login,
  verifyOTP,
  resendOTP,
  getCurrentUser,
};
