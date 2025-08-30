const fs = require('fs');
const path = require('path');

// Check if .env file exists
const envPath = path.join(__dirname, '.env');
const envExamplePath = path.join(__dirname, 'env.example');

if (!fs.existsSync(envPath)) {
  console.log('📝 Creating .env file from env.example...');
  
  // Read the example file
  const envExample = fs.readFileSync(envExamplePath, 'utf8');
  
  // Create a basic .env for development
  const envContent = `# Database Configuration
DATABASE_URL="postgresql://postgres:password@localhost:5432/greenshield?sslmode=disable"

# JWT Configuration
JWT_SECRET="dev-jwt-secret-key-change-in-production"

# Email Configuration (Gmail) - Update these with your actual email
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_USER="your-email@gmail.com"
EMAIL_PASS="your-app-password"

# Server Configuration
PORT=5000
NODE_ENV="development"

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
`;

  fs.writeFileSync(envPath, envContent);
  console.log('✅ .env file created successfully!');
  console.log('⚠️  Please update the EMAIL_USER and EMAIL_PASS in .env with your actual email credentials');
} else {
  console.log('✅ .env file already exists');
}

console.log('\n🚀 To start the server, run: npm start');
console.log('🔧 For development with auto-restart, run: npm run dev');
