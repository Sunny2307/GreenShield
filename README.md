# 🌿 GreenShield - Environmental Protection App

A comprehensive React Native mobile application designed to protect mangrove ecosystems and report environmental incidents. Built with a robust Node.js/Express backend and PostgreSQL database.

![GreenShield Banner](https://img.shields.io/badge/React%20Native-0.72-blue?style=for-the-badge&logo=react)
![Node.js](https://img.shields.io/badge/Node.js-18+-green?style=for-the-badge&logo=node.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 📱 Features

### 🔐 User Authentication
- **Secure Signup/Login** with email verification
- **OTP Verification** system for enhanced security
- **JWT-based authentication** with token management
- **Password recovery** functionality

### 📊 Interactive Dashboard
- **User Statistics** - Total reports, validated incidents, points earned
- **Community Reports Feed** - Real-time updates from other users
- **Achievement Badges** - Gamification system for environmental contributions
- **Quick Actions** - Easy access to report incidents and view history

### 📸 Incident Reporting System
- **Photo Upload** - Camera and gallery integration with image compression
- **Real-time GPS Location** - Automatic location detection with Google Maps
- **Category Selection** - Illegal cutting, waste dumping, pollution, and more
- **Interactive Map Preview** - Visual location confirmation
- **Offline Support** - Graceful fallbacks when services are unavailable

### 🗺️ Location Services
- **GPS Integration** - Real-time location tracking
- **Google Maps API** - Interactive map display and geocoding
- **Address Resolution** - Convert coordinates to readable addresses
- **Location Permissions** - Smart permission handling for Android/iOS

### 🔧 Advanced Features
- **Points System** - Earn points for environmental contributions
- **Report Management** - View, edit, and delete your reports
- **Community Engagement** - View reports from other users
- **Debug Tools** - Built-in location service testing
- **Error Handling** - Comprehensive error management and user feedback

## 🛠️ Technology Stack

### Frontend (React Native)
- **React Native 0.72** - Cross-platform mobile development
- **React Navigation 6** - Screen navigation and routing
- **React Native Maps** - Google Maps integration
- **React Native Image Picker** - Camera and gallery access
- **React Native Geolocation** - GPS services
- **Expo Vector Icons** - Icon library

### Backend (Node.js/Express)
- **Node.js 18+** - Runtime environment
- **Express.js 4** - Web framework
- **PostgreSQL 15+** - Relational database
- **Prisma ORM** - Database management and migrations
- **JWT** - Authentication and authorization
- **Express Validator** - Input validation and sanitization
- **Nodemailer** - Email service integration

### Development Tools
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Jest** - Testing framework
- **Metro** - React Native bundler

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **React Native CLI**
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)
- **PostgreSQL** database
- **Google Maps API key**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sunny2307/GreenShield.git
   cd GreenShield
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd GreenShields
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   cd ../backend
   npm install
   ```

4. **Environment Configuration**

   **Frontend** (`GreenShields/src/config/config.js`):
   ```javascript
   export const API_BASE_URL = 'http://your-backend-url:3000/api';
   ```
   
   **Backend** (`backend/.env`):
   ```env
   DATABASE_URL="postgresql://username:password@localhost:5432/greenshield"
   JWT_SECRET="your-super-secret-jwt-key"
   EMAIL_SERVICE_API_KEY="your-email-service-key"
   PORT=3000
   NODE_ENV=development
   ```

5. **Database Setup**
   ```bash
   cd backend
   npx prisma migrate dev --name init
   npx prisma generate
   ```

6. **Google Maps Configuration**
   - Get API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Maps SDK for Android/iOS and Geocoding API
   - Update `GreenShields/src/config/maps.js`:
   ```javascript
   export const GOOGLE_MAPS_API_KEY = 'your-google-maps-api-key';
   ```

7. **Run the Application**

   **Backend Server:**
   ```bash
   cd backend
   npm start
   ```

   **Frontend App:**
   ```bash
   cd GreenShields
   npx react-native run-android
   # or for iOS
   npx react-native run-ios
   ```

## 📱 App Screenshots

### Dashboard
- User statistics and quick actions
- Community reports feed with real-time updates
- Achievement badges and progress tracking

### Report Incident
- Photo upload with camera/gallery options
- Real-time GPS location with map preview
- Category selection for different incident types
- Rich text description input

### Authentication
- Secure login and signup screens
- OTP verification for enhanced security
- Password recovery functionality

## 🔧 Configuration

### Android Permissions
Add to `GreenShields/android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.INTERNET" />

<!-- Google Maps API Key -->
<meta-data
  android:name="com.google.android.geo.API_KEY"
  android:value="your-google-maps-api-key" />
```

### iOS Permissions
Add to `GreenShields/ios/GreenShields/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to capture incident photos</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs photo library access to select incident photos</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access to accurately report incident locations</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs location access to accurately report incident locations</string>
```

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | User registration |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/verify-otp` | OTP verification |
| `POST` | `/api/auth/resend-otp` | Resend OTP |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/reports` | Submit incident report |
| `GET` | `/api/reports` | Get user reports |
| `GET` | `/api/reports/community` | Get community reports |
| `GET` | `/api/reports/:id` | Get specific report |
| `PUT` | `/api/reports/:id` | Update report |
| `DELETE` | `/api/reports/:id` | Delete report |

## 🏗️ Project Structure

```
GreenShield/
├── GreenShields/                 # React Native Frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   └── Toast.jsx        # Toast notification component
│   │   ├── screens/             # App screens
│   │   │   ├── LoginScreen.jsx
│   │   │   ├── SignupScreen.jsx
│   │   │   ├── DashboardScreen.jsx
│   │   │   ├── ReportIncidentScreen.jsx
│   │   │   └── TestLocationScreen.jsx
│   │   ├── navigation/          # Navigation setup
│   │   │   └── AppNavigator.jsx
│   │   ├── services/            # API services
│   │   │   └── api.js
│   │   ├── config/              # Configuration files
│   │   │   ├── config.js        # API configuration
│   │   │   └── maps.js          # Google Maps configuration
│   │   └── utils/               # Utility functions
│   │       └── locationDebug.js # Location debugging tools
│   ├── android/                 # Android specific files
│   └── ios/                     # iOS specific files
├── backend/                     # Node.js Backend
│   ├── controllers/             # Route controllers
│   │   ├── authController.js    # Authentication logic
│   │   └── reportsController.js # Reports management
│   ├── middleware/              # Custom middleware
│   │   ├── auth.js              # JWT authentication
│   │   └── validation.js        # Input validation
│   ├── routes/                  # API routes
│   │   ├── auth.js              # Auth routes
│   │   └── reports.js           # Reports routes
│   ├── prisma/                  # Database schema
│   │   └── schema.prisma        # Database models
│   ├── utils/                   # Utility functions
│   │   └── emailService.js      # Email service
│   ├── config/                  # Backend configuration
│   │   └── database.js          # Database connection
│   └── server.js                # Main server file
├── docs/                        # Documentation
├── .gitignore                   # Git ignore rules
├── README.md                    # Project documentation
└── LICENSE                      # MIT License
```

## 🐛 Troubleshooting

### Common Issues

1. **Location Services Not Working**
   - Check device GPS settings
   - Verify Google Maps API key configuration
   - Use the built-in test screen: Dashboard → "🔧 Test Location Services"
   - Check console logs for detailed error messages

2. **Photo Upload Failing**
   - Check camera/gallery permissions
   - Ensure sufficient storage space
   - Verify image size limits (max 1024x1024)
   - Check network connectivity

3. **Backend Connection Issues**
   - Verify `API_BASE_URL` in `src/config/config.js`
   - Check backend server is running on correct port
   - Verify database connection in backend
   - Check firewall and network settings

4. **Database Migration Issues**
   ```bash
   cd backend
   npx prisma migrate reset
   npx prisma migrate dev --name init
   npx prisma generate
   ```

### Debug Tools
The app includes comprehensive debugging tools:
1. **Location Test Screen** - Test GPS and Maps functionality
2. **Console Logging** - Detailed error messages and debugging info
3. **Error Handling** - Graceful fallbacks for all services
4. **Toast Notifications** - User-friendly error messages

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Input Validation** - Comprehensive validation for all inputs
- **SQL Injection Protection** - Prisma ORM with parameterized queries
- **XSS Protection** - Input sanitization and output encoding
- **Rate Limiting** - API rate limiting to prevent abuse
- **Environment Variables** - Secure configuration management

## 📈 Performance Optimizations

- **Image Compression** - Automatic image optimization
- **Lazy Loading** - Efficient component loading
- **Caching** - API response caching
- **Database Indexing** - Optimized database queries
- **Bundle Optimization** - Metro bundler optimizations

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Maps API** - Location services and mapping
- **React Native Community** - Excellent documentation and support
- **Environmental Protection Organizations** - Inspiration and guidance
- **Open Source Contributors** - Libraries and tools used

## 📞 Support

For support and questions:
- 📧 **Create an issue** in the GitHub repository
- 📖 **Check the troubleshooting guide** above
- 🔧 **Use the debug tools** built into the app
- 📚 **Review the API documentation** in this README

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐️ on GitHub!

---

**Made with ❤️ for environmental protection and mangrove ecosystem conservation**

*GreenShield - Protecting our planet, one report at a time*
