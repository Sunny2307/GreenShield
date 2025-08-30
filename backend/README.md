# GreenShield Backend

A secure authentication backend with email OTP verification built with Node.js, Express, Prisma, and PostgreSQL.

## Features

- 🔐 User authentication with JWT tokens
- 📧 Email OTP verification using Nodemailer
- 🛡️ Password hashing with bcrypt
- 📊 PostgreSQL database with Prisma ORM
- ✅ Input validation with express-validator
- 🚦 Rate limiting for security
- 🔒 CORS and security headers
- 📝 Comprehensive error handling

## Prerequisites

- Node.js (v16 or higher)
- PostgreSQL database (Neon DB recommended)
- Gmail account for email service

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Environment Configuration

Copy the example environment file and configure your variables:

```bash
cp env.example .env
```

Update the `.env` file with your actual values:

```env
# Database Configuration (Neon DB)
DATABASE_URL="postgresql://username:password@host:port/database?sslmode=require"

# JWT Configuration
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
JWT_EXPIRES_IN="7d"

# Email Configuration (Gmail)
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_USER="your-email@gmail.com"
EMAIL_PASS="your-app-password"

# Server Configuration
PORT=5000
NODE_ENV="development"
```

### 3. Database Setup

#### Using Neon DB (Recommended)

1. Create a free account at [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string to your `.env` file
4. Run the database migration:

```bash
npx prisma db push
```

#### Using Local PostgreSQL

1. Install PostgreSQL locally
2. Create a database
3. Update the `DATABASE_URL` in your `.env` file
4. Run the migration:

```bash
npx prisma db push
```

### 4. Email Service Setup

#### Gmail App Password

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. Use this password in your `.env` file as `EMAIL_PASS`

### 5. Start the Server

```bash
# Development mode
npm run dev

# Production mode
npm start
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication Routes

#### POST `/api/auth/signup`
Register a new user with email verification.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully. Please check your email for verification code.",
  "data": {
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "isEmailVerified": false,
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "emailSent": true
  }
}
```

#### POST `/api/auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "isEmailVerified": true,
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "jwt_token_here"
  }
}
```

#### POST `/api/auth/verify-otp`
Verify email with OTP code.

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "data": {
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "isEmailVerified": true,
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "jwt_token_here"
  }
}
```

#### POST `/api/auth/resend-otp`
Resend OTP to email.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "New verification code sent to your email"
}
```

#### GET `/api/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer jwt_token_here
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "isEmailVerified": true,
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  }
}
```

### Health Check

#### GET `/health`
Check server status.

**Response:**
```json
{
  "success": true,
  "message": "GreenShield Backend is running",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "environment": "development"
}
```

## Validation Rules

### Signup Validation
- **Name**: 2-50 characters, letters and spaces only
- **Email**: Valid email format
- **Password**: Minimum 6 characters, must contain uppercase, lowercase, and number

### Login Validation
- **Email**: Valid email format
- **Password**: Required

### OTP Validation
- **Email**: Valid email format
- **OTP**: Exactly 6 digits

## Rate Limiting

- **Auth routes**: 5 requests per 15 minutes per IP
- **OTP routes**: 3 requests per 5 minutes per IP
- **Global**: 100 requests per 15 minutes per IP

## Security Features

- Password hashing with bcrypt (12 salt rounds)
- JWT token authentication
- CORS protection
- Helmet security headers
- Rate limiting
- Input validation and sanitization
- SQL injection protection (Prisma)
- XSS protection

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    {
      "field": "email",
      "message": "Please provide a valid email address"
    }
  ]
}
```

## Development

### Available Scripts

```bash
# Start development server
npm run dev

# Start production server
npm start

# Generate Prisma client
npm run db:generate

# Push database schema
npm run db:push

# Open Prisma Studio
npm run db:studio
```

### Database Management

```bash
# View database in browser
npm run db:studio

# Reset database (development only)
npx prisma db push --force-reset
```

## Production Deployment

1. Set `NODE_ENV=production` in your environment
2. Use a strong `JWT_SECRET`
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use environment-specific database URLs
6. Set up proper logging and monitoring

## Troubleshooting

### Common Issues

1. **Email not sending**: Check Gmail app password and 2FA settings
2. **Database connection failed**: Verify DATABASE_URL and network connectivity
3. **OTP not working**: Check email service configuration
4. **CORS errors**: Update CORS configuration for your frontend domain

### Logs

Check the console output for detailed error messages and debugging information.

## License

ISC
