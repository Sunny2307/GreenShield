# GreenShield - Environmental Protection App

A React Native mobile application for reporting environmental incidents and protecting mangrove ecosystems. Built with a Node.js/Express backend and PostgreSQL database.

## 🌿 Features

### Frontend (React Native)
- **User Authentication**: Signup, login, and OTP verification
- **Dashboard**: User statistics, community reports, and badges
- **Incident Reporting**: Photo upload, GPS location, and category selection
- **Real-time Location**: GPS tracking with Google Maps integration
- **Photo Capture**: Camera and gallery integration
- **Offline Support**: Graceful fallbacks for location services

### Backend (Node.js/Express)
- **RESTful API**: Complete CRUD operations for reports
- **Authentication**: JWT-based user authentication
- **Database**: PostgreSQL with Prisma ORM
- **File Upload**: Base64 image storage
- **Points System**: User rewards for environmental contributions
- **Validation**: Comprehensive input validation and error handling

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- React Native CLI
- Android Studio / Xcode
- PostgreSQL database
- Google Maps API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/greenshield.git
   cd greenshield
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

4. **Environment Setup**
   
   **Frontend** (`GreenShields/src/config/config.js`):
   ```javascript
   export const API_BASE_URL = 'http://your-backend-url:3000/api';
   ```
   
   **Backend** (`backend/.env`):
   ```env
   DATABASE_URL="postgresql://username:password@localhost:5432/greenshield"
   JWT_SECRET="your-jwt-secret"
   EMAIL_SERVICE_API_KEY="your-email-service-key"
   ```

5. **Database Setup**
   ```bash
   cd backend
   npx prisma migrate dev
   npx prisma generate
   ```

6. **Google Maps Setup**
   - Get API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Maps SDK for Android/iOS and Geocoding API
   - Update `GreenShields/src/config/maps.js`

7. **Run the Application**
   
   **Backend:**
   ```bash
   cd backend
   npm start
   ```
   
   **Frontend:**
   ```bash
   cd GreenShields
   npx react-native run-android
   # or
   npx react-native run-ios
   ```

## 📱 App Screenshots

### Dashboard
- User statistics and quick actions
- Community reports feed
- Achievement badges

### Report Incident
- Photo upload (camera/gallery)
- Real-time GPS location
- Interactive map preview
- Category selection
- Description input

## 🛠️ Technology Stack

### Frontend
- **React Native** - Cross-platform mobile development
- **React Navigation** - Screen navigation
- **React Native Maps** - Google Maps integration
- **React Native Image Picker** - Camera and gallery access
- **React Native Geolocation** - GPS services

### Backend
- **Node.js** - Runtime environment
- **Express.js** - Web framework
- **PostgreSQL** - Database
- **Prisma** - Database ORM
- **JWT** - Authentication
- **Express Validator** - Input validation

## 🔧 Configuration

### Android Permissions
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.INTERNET" />
```

### iOS Permissions
Add to `ios/GreenShields/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access for incident photos</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access for incident reporting</string>
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-otp` - OTP verification
- `POST /api/auth/resend-otp` - Resend OTP

### Reports
- `POST /api/reports` - Submit incident report
- `GET /api/reports` - Get user reports
- `GET /api/reports/community` - Get community reports
- `GET /api/reports/:id` - Get specific report
- `PUT /api/reports/:id` - Update report
- `DELETE /api/reports/:id` - Delete report

## 🏗️ Project Structure

```
GreenShield/
├── GreenShields/                 # React Native Frontend
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── screens/             # App screens
│   │   ├── navigation/          # Navigation setup
│   │   ├── services/            # API services
│   │   ├── config/              # Configuration files
│   │   └── utils/               # Utility functions
│   ├── android/                 # Android specific files
│   └── ios/                     # iOS specific files
├── backend/                     # Node.js Backend
│   ├── controllers/             # Route controllers
│   ├── middleware/              # Custom middleware
│   ├── routes/                  # API routes
│   ├── prisma/                  # Database schema
│   └── utils/                   # Utility functions
└── docs/                        # Documentation
```

## 🐛 Troubleshooting

### Common Issues

1. **Location Services Not Working**
   - Check device GPS settings
   - Verify Google Maps API key
   - Use the built-in test screen for debugging

2. **Photo Upload Failing**
   - Check camera/gallery permissions
   - Ensure sufficient storage space
   - Verify image size limits

3. **Backend Connection Issues**
   - Check API_BASE_URL configuration
   - Verify backend server is running
   - Check network connectivity

### Debug Tools
The app includes a built-in test screen for debugging location services:
1. Go to Dashboard
2. Tap "🔧 Test Location Services"
3. Run individual tests to identify issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Maps API for location services
- React Native community for excellent documentation
- Environmental protection organizations for inspiration

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting guide
- Review the API documentation

---

**Made with ❤️ for environmental protection**
