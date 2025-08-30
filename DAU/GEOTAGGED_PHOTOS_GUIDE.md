# 📸 Geotagged Photo Processing Guide

## 🎯 Overview

The Community Mangrove Watch API has been updated to **require geotagged photos** and automatically extract GPS coordinates from them. This ensures data accuracy and simplifies the reporting process.

## 🔄 What Changed

### **Before (Old API):**
```json
{
    "photo_url": "http://localhost:8080/photo.jpg",
    "latitude": 12.345678,    // User had to provide coordinates
    "longitude": 78.901234,   // User had to provide coordinates
    "timestamp": "2024-01-15T10:30:00Z",
    "description": "Suspicious activity",
    "reporter_id": "user_001"
}
```

### **After (New API):**
```json
{
    "photo_url": "http://localhost:8080/geotagged_photo.jpg",  // MUST be geotagged
    "timestamp": "2024-01-15T10:30:00Z",
    "description": "Suspicious activity",
    "reporter_id": "user_001"
}
// Coordinates are automatically extracted from the photo!
```

## ✅ New Requirements

### **Required Fields:**
- ✅ `photo_url` - **MUST be a geotagged photo**
- ✅ `timestamp` - ISO format timestamp
- ✅ `reporter_id` - Unique user identifier

### **Optional Fields:**
- ❓ `description` - Description of the incident

### **No Longer Needed:**
- ❌ `latitude` - Extracted from photo
- ❌ `longitude` - Extracted from photo

## 📱 How to Create Geotagged Photos

### **Method 1: Smartphone (Recommended)**
1. **Enable GPS/Location Services** on your phone
2. **Open Camera App**
3. **Take Photo** - GPS coordinates are automatically embedded
4. **Upload to File Server** - Use your local file server

### **Method 2: Digital Camera**
1. **Enable GPS** on your camera (if supported)
2. **Take Photo** with GPS enabled
3. **Transfer to Computer**
4. **Upload to File Server**

### **Method 3: Manual Geotagging**
1. **Take Photo** normally
2. **Use Geotagging Software** (like GeoSetter, ExifTool)
3. **Add GPS Coordinates** manually
4. **Upload to File Server**

## 🧪 Testing the New API

### **Valid Request (Geotagged Photo):**
```json
{
    "photo_url": "http://localhost:8080/geotagged_photo.jpg",
    "timestamp": "2024-01-15T10:30:00Z",
    "description": "Suspicious mangrove cutting activity",
    "reporter_id": "citizen_001"
}
```

### **Invalid Request (Non-geotagged Photo):**
```json
{
    "photo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
    "timestamp": "2024-01-15T10:30:00Z",
    "description": "This will fail - photo not geotagged",
    "reporter_id": "citizen_002"
}
```

**Expected Error:**
```json
{
    "error": "Photo processing failed: Photo is not geotagged. Please upload a photo with GPS coordinates."
}
```

### **Invalid Request (Missing Photo):**
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "description": "This will fail - no photo",
    "reporter_id": "citizen_003"
}
```

**Expected Error:**
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "photo_url"],
            "msg": "Field required"
        }
    ]
}
```

## 🔍 How It Works

### **1. Photo Upload**
- User uploads photo to file server
- Photo URL is provided to API

### **2. GPS Extraction**
- System downloads photo
- Extracts EXIF data
- Reads GPS coordinates from EXIF tags

### **3. Coordinate Validation**
- Validates coordinate ranges (-90 to 90, -180 to 180)
- Checks for reasonable values

### **4. Processing**
- Uses extracted coordinates for satellite data
- Processes photo through AI models
- Returns validation results

## 📊 Response Format

### **Successful Response:**
```json
{
    "report_id": "report_20240115_103000_citizen_001",
    "reporter_id": "citizen_001",
    "timestamp": "2024-01-15T10:30:00Z",
    "confidence_score": 0.85,
    "confidence_level": "High",
    "anomaly_detected": false,
    "anomaly_score": 0.23,
    "urgency_level": "low",
    "citizen_confidence": 0.82,
    "satellite_confidence": 0.88,
    "inference_time": 2.1,
    "summary": "High confidence report processed successfully...",
    "recommendations": [
        "Monitor area for additional reports",
        "Schedule routine inspection"
    ],
    "points_earned": 50,
    "badges": ["First Report", "High Quality"],
    "processing_metadata": {
        "model_used": "Swin-UMamba",
        "satellite_data_source": "mock_sentinel2",
        "cloud_coverage": 0.05,
        "processing_time": 2.1,
        "image_quality_score": 0.85,
        "coordinates_source": "photo_gps",
        "extracted_coordinates": {
            "latitude": 21.9497,
            "longitude": 89.1833
        }
    }
}
```

## 🛠️ Technical Details

### **Supported Photo Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)

### **EXIF GPS Tags Extracted:**
- `GPSLatitude` - Latitude coordinates
- `GPSLongitude` - Longitude coordinates
- `GPSLatitudeRef` - N/S reference
- `GPSLongitudeRef` - E/W reference

### **Coordinate Conversion:**
- Converts from degrees/minutes/seconds to decimal degrees
- Handles N/S and E/W references
- Validates coordinate ranges

## 🚨 Error Handling

### **Common Errors:**

1. **Photo Not Geotagged:**
   ```
   Photo is not geotagged. Please upload a photo with GPS coordinates.
   ```

2. **Invalid Photo Format:**
   ```
   Unsupported file format: .gif. Supported formats: .jpg, .jpeg, .png, .tiff, .tif
   ```

3. **Photo Quality Too Low:**
   ```
   Photo quality too low (0.23). Please upload a clearer photo.
   ```

4. **Invalid GPS Coordinates:**
   ```
   Invalid GPS coordinates: (100.0, 200.0)
   ```

## 📋 Testing Checklist

### **For Developers:**
- [ ] Test with geotagged photos
- [ ] Test with non-geotagged photos
- [ ] Test with missing photo URL
- [ ] Test with invalid photo formats
- [ ] Test with low-quality photos
- [ ] Verify coordinate extraction accuracy

### **For Users:**
- [ ] Enable GPS on device
- [ ] Take photos with location services
- [ ] Upload to file server
- [ ] Use correct API format
- [ ] Check response for success

## 🎯 Benefits

### **For Users:**
- ✅ **Simplified Process** - No need to manually enter coordinates
- ✅ **Higher Accuracy** - GPS coordinates are precise
- ✅ **Reduced Errors** - No manual coordinate entry mistakes
- ✅ **Better Quality** - System validates photo quality

### **For System:**
- ✅ **Data Integrity** - Coordinates come from photo metadata
- ✅ **Automated Validation** - Built-in quality checks
- ✅ **Consistent Format** - Standardized coordinate extraction
- ✅ **Error Prevention** - Validates geotagging before processing

## 🔧 Implementation Notes

### **Dependencies Added:**
- `piexif>=1.1.3` - EXIF data extraction
- Enhanced PIL/Pillow usage for EXIF handling

### **Files Modified:**
- `src/preprocessing/photo_processor.py` - New photo processing module
- `src/preprocessing/report_processor.py` - Updated to use photo processor
- `src/api/main.py` - Updated API requirements
- `requirements_simple.txt` - Added piexif dependency

### **Backward Compatibility:**
- ❌ **Breaking Change** - Photo URL is now required
- ❌ **Breaking Change** - Latitude/longitude fields removed
- ✅ **Enhanced Error Messages** - Better user feedback
- ✅ **Improved Validation** - More robust error handling

---

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements_simple.txt
   ```

2. **Start File Server:**
   ```bash
   python simple_file_server.py
   ```

3. **Start API Server:**
   ```bash
   python -m uvicorn src.api.main:app --host localhost --port 8000 --reload
   ```

4. **Test with Geotagged Photos:**
   ```bash
   python test_geotagged_photos.py
   ```

5. **Use in Postman:**
   - Use the new API format
   - Upload geotagged photos to file server
   - Test with various scenarios

---

**🎉 The system now ensures data accuracy by requiring geotagged photos and automatically extracting coordinates!**
