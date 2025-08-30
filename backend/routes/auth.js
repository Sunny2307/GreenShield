const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');

// Import controllers
const {
  signup,
  login,
  verifyOTP,
  resendOTP,
  getCurrentUser,
} = require('../controllers/authController');

// Import middleware
const {
  authenticateToken,
  requireEmailVerification,
} = require('../middleware/auth');

const {
  signupValidation,
  loginValidation,
  otpValidation,
  resendOtpValidation,
  handleValidationErrors,
} = require('../middleware/validation');

// Rate limiting for auth routes
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: {
    success: false,
    message: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

const otpLimiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5 minutes
  max: 3, // limit each IP to 3 OTP requests per windowMs
  message: {
    success: false,
    message: 'Too many OTP requests, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Routes
// POST /api/auth/signup
router.post('/signup', authLimiter, signupValidation, handleValidationErrors, signup);

// POST /api/auth/login
router.post('/login', authLimiter, loginValidation, handleValidationErrors, login);

// POST /api/auth/verify-otp
router.post('/verify-otp', otpLimiter, otpValidation, handleValidationErrors, verifyOTP);

// POST /api/auth/resend-otp
router.post('/resend-otp', otpLimiter, resendOtpValidation, handleValidationErrors, resendOTP);

// GET /api/auth/me (protected route)
router.get('/me', authenticateToken, getCurrentUser);

module.exports = router;
