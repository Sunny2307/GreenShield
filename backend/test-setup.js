require('dotenv').config();
const { testConnection } = require('./config/database');
const { verifyTransporter } = require('./utils/emailService');

async function testSetup() {
  console.log('🧪 Testing GreenShield Backend Setup...\n');

  // Test 1: Environment Variables
  console.log('1. Checking Environment Variables...');
  const requiredEnvVars = [
    'DATABASE_URL',
    'JWT_SECRET',
    'EMAIL_HOST',
    'EMAIL_USER',
    'EMAIL_PASS'
  ];

  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missingVars.length > 0) {
    console.log('❌ Missing environment variables:', missingVars.join(', '));
    console.log('📝 Please copy env.example to .env and fill in your values\n');
    return false;
  } else {
    console.log('✅ All required environment variables are set\n');
  }

  // Test 2: Database Connection
  console.log('2. Testing Database Connection...');
  try {
    await testConnection();
    console.log('✅ Database connection successful\n');
  } catch (error) {
    console.log('❌ Database connection failed:', error.message);
    console.log('📝 Please check your DATABASE_URL in .env file\n');
    return false;
  }

  // Test 3: Email Service
  console.log('3. Testing Email Service...');
  try {
    await verifyTransporter();
    console.log('✅ Email service configuration is valid\n');
  } catch (error) {
    console.log('❌ Email service configuration failed:', error.message);
    console.log('📝 Please check your email settings in .env file\n');
    return false;
  }

  // Test 4: Prisma Client
  console.log('4. Testing Prisma Client...');
  try {
    const { PrismaClient } = require('@prisma/client');
    const prisma = new PrismaClient();
    await prisma.$connect();
    console.log('✅ Prisma client is working\n');
    await prisma.$disconnect();
  } catch (error) {
    console.log('❌ Prisma client test failed:', error.message);
    console.log('📝 Try running: npx prisma generate\n');
    return false;
  }

  console.log('🎉 All tests passed! Your backend is ready to use.');
  console.log('\n📋 Next steps:');
  console.log('1. Run: npm run dev (to start development server)');
  console.log('2. Test the API endpoints with your frontend or Postman');
  console.log('3. Check the README.md for API documentation');
  
  return true;
}

// Run the test
testSetup().catch(console.error);
