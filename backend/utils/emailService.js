const nodemailer = require('nodemailer');

// Create transporter
const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: process.env.EMAIL_PORT,
  secure: false, // true for 465, false for other ports
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// Generate OTP
function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

// Send OTP email
async function sendOTPEmail(email, otp, name) {
  try {
    const mailOptions = {
      from: `"GreenShield" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: 'Email Verification - GreenShield',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
          <div style="background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #2e7d32; text-align: center; margin-bottom: 30px;">GreenShield Email Verification</h2>
            
            <p style="font-size: 16px; color: #333; margin-bottom: 20px;">Hello ${name},</p>
            
            <p style="font-size: 16px; color: #333; margin-bottom: 20px;">Thank you for signing up with GreenShield! To complete your registration, please use the following verification code:</p>
            
            <div style="background-color: #e8f5e8; padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0;">
              <h1 style="color: #2e7d32; font-size: 32px; letter-spacing: 5px; margin: 0;">${otp}</h1>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-bottom: 20px;">This code will expire in 10 minutes for security reasons.</p>
            
            <p style="font-size: 14px; color: #666; margin-bottom: 20px;">If you didn't create an account with GreenShield, please ignore this email.</p>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
              <p style="font-size: 12px; color: #999;">© 2024 GreenShield. All rights reserved.</p>
            </div>
          </div>
        </div>
      `,
    };

    const info = await transporter.sendMail(mailOptions);
    console.log('Email sent successfully:', info.messageId);
    return true;
  } catch (error) {
    console.error('Error sending email:', error);
    return false;
  }
}

// Verify transporter
async function verifyTransporter() {
  try {
    await transporter.verify();
    console.log('✅ Email service is ready');
    return true;
  } catch (error) {
    console.error('❌ Email service configuration error:', error);
    return false;
  }
}

module.exports = {
  generateOTP,
  sendOTPEmail,
  verifyTransporter,
};
