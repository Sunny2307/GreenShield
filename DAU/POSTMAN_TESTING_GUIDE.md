# Postman Testing Guide - Community Mangrove Watch API

This guide will walk you through testing all API endpoints using Postman.

## Prerequisites

1. **Install Postman** (if not already installed)
   - Download from: https://www.postman.com/downloads/
   - Create a free account

2. **Start the API Server**
   ```bash
   # In your project directory
   python -m uvicorn src.api.main:app --host localhost --port 8000 --reload
   ```

3. **Verify API is Running**
   - Open browser and go to: http://localhost:8000
   - You should see: `{"message": "Community Mangrove Watch API", "version": "1.0.0", "status": "operational", "docs": "/docs"}`

---

## Step 1: Test Basic Connectivity

### **GET** - Root Endpoint

**Request:**
- **Method:** GET
- **URL:** `http://localhost:8000/`
- **Headers:** None required

**Expected Response:**
```json
{
  "message": "Community Mangrove Watch API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs"
}
```

**Postman Setup:**
1. Open Postman
2. Click "New" → "Request"
3. Set method to **GET**
4. Enter URL: `http://localhost:8000/`
5. Click "Send"

---

## Step 2: Test Health Check

### **GET** - Health Check

**Request:**
- **Method:** GET
- **URL:** `http://localhost:8000/health`
- **Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "report_processor": "healthy",
    "satellite_fetcher": "healthy",
    "mangrove_validator": "healthy",
    "result_processor": "healthy"
  }
}
```

**Postman Setup:**
1. Create new request
2. Set method to **GET**
3. Enter URL: `http://localhost:8000/health`
4. Click "Send"

---

## Step 3: Test Connection

### **POST** - Test Connection

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/test-connection`
- **Headers:** 
  - `Content-Type: application/json`
- **Body:** None required

**Expected Response:**
```json
{
  "status": "connected",
  "pipeline_ready": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "API is operational"
}
```

**Postman Setup:**
1. Create new request
2. Set method to **POST**
3. Enter URL: `http://localhost:8000/test-connection`
4. Go to "Headers" tab
5. Add header: `Content-Type: application/json`
6. Click "Send"

---

## Step 4: Test Main Endpoint - Valid Report

### **POST** - Validate Report (With Photo)

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/validate-report`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "photo_url": "https://example.com/mangrove_photo.jpg",
  "latitude": 12.345678,
  "longitude": 78.901234,
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Suspicious mangrove cutting activity detected. Large trees have been removed and there are signs of recent heavy machinery activity.",
  "reporter_id": "citizen_001"
}
```

**Expected Response:**
```json
{
  "report_id": "report_20240115_103000_citizen_001",
  "reporter_id": "citizen_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "confidence_score": 0.85,
  "confidence_level": "High",
  "anomaly_detected": true,
  "anomaly_score": 0.72,
  "urgency_level": "High",
  "citizen_confidence": 0.88,
  "satellite_confidence": 0.82,
  "inference_time": 2.34,
  "summary": "High confidence anomaly detected. Citizen photo shows significant mangrove loss compared to satellite imagery. Urgent investigation recommended.",
  "recommendations": [
    "Dispatch field team for immediate investigation",
    "Contact local authorities",
    "Document the area for legal proceedings"
  ],
  "points_earned": 75,
  "badges": ["Anomaly Detector", "High Quality"],
  "processing_metadata": {
    "model_used": "Swin-UMamba",
    "satellite_data_source": "Sentinel-2",
    "cloud_coverage": 0.05,
    "processing_time": 2.34,
    "image_quality_score": 0.92
  }
}
```

**Postman Setup:**
1. Create new request
2. Set method to **POST**
3. Enter URL: `http://localhost:8000/validate-report`
4. Go to "Headers" tab
5. Add header: `Content-Type: application/json`
6. Go to "Body" tab
7. Select "raw" and "JSON"
8. Paste the JSON body above
9. Click "Send"

---

## Step 5: Test Report Without Photo

### **POST** - Validate Report (No Photo)

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/validate-report`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "latitude": 12.345678,
  "longitude": 78.901234,
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Report without photo - heard chainsaw sounds from mangrove area",
  "reporter_id": "citizen_002"
}
```

**Expected Response:**
```json
{
  "report_id": "report_20240115_103000_citizen_002",
  "reporter_id": "citizen_002",
  "timestamp": "2024-01-15T10:30:00Z",
  "confidence_score": 0.45,
  "confidence_level": "Medium",
  "anomaly_detected": false,
  "anomaly_score": 0.23,
  "urgency_level": "Medium",
  "citizen_confidence": 0.0,
  "satellite_confidence": 0.45,
  "inference_time": 1.85,
  "summary": "Medium confidence report without photo evidence. Satellite data shows normal conditions. Further investigation recommended.",
  "recommendations": [
    "Request photo evidence if possible",
    "Schedule field visit to verify",
    "Monitor area for additional reports"
  ],
  "points_earned": 25,
  "badges": ["First Report"],
  "processing_metadata": {
    "model_used": "Swin-UMamba",
    "satellite_data_source": "Sentinel-2",
    "cloud_coverage": 0.08,
    "processing_time": 1.85,
    "image_quality_score": 0.0
  }
}
```

---

## Step 6: Test Error Handling

### **POST** - Invalid Coordinates

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/validate-report`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "photo_url": "https://example.com/photo.jpg",
  "latitude": 100.0,
  "longitude": 78.901234,
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Test report with invalid coordinates",
  "reporter_id": "test_user"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "HTTP error",
  "message": {
    "error": "Invalid input data",
    "errors": ["Invalid latitude: 100.0"],
    "warnings": []
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/validate-report"
}
```

---

## Step 7: Test Missing Required Fields

### **POST** - Missing Required Fields

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/validate-report`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "latitude": 12.345678,
  "longitude": 78.901234
}
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "timestamp"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "reporter_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Step 8: Test Status Endpoint

### **GET** - Pipeline Status

**Request:**
- **Method:** GET
- **URL:** `http://localhost:8000/status`
- **Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "report_processor": "healthy",
    "satellite_fetcher": "healthy",
    "mangrove_validator": "healthy",
    "result_processor": "healthy"
  },
  "configuration": {
    "satellite_source": "sentinel_hub",
    "model_path": "models/swin_umamba_mangrove.pth",
    "api_debug": true
  },
  "model_info": {
    "segmentation_model": "Swin-UMamba",
    "anomaly_detector": "IsolationForest",
    "model_status": "loaded"
  }
}
```

---

## Step 9: Test Statistics Endpoint

### **GET** - Processing Statistics

**Request:**
- **Method:** GET
- **URL:** `http://localhost:8000/statistics`
- **Headers:** None required

**Expected Response:**
```json
{
  "statistics": {
    "total_reports_processed": 2,
    "successful_reports": 2,
    "failed_reports": 0,
    "success_rate": 1.0,
    "average_processing_time": 2.095,
    "anomalies_detected": 1,
    "total_points_awarded": 100,
    "unique_reporters": 2
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Step 10: Create Postman Collection

### **Import Collection**

1. **Create Collection:**
   - In Postman, click "New" → "Collection"
   - Name it: "Community Mangrove Watch API"

2. **Add All Requests:**
   - Right-click collection → "Add Request"
   - Create requests for each endpoint above

3. **Save Collection:**
   - Right-click collection → "Export"
   - Save as JSON file

### **Environment Variables (Optional)**

Create an environment for easy testing:

1. **Create Environment:**
   - Click "Environments" → "New"
   - Name: "Local Development"

2. **Add Variables:**
   - `base_url`: `http://localhost:8000`
   - `api_key`: (if you add authentication later)

3. **Use Variables:**
   - In requests, use: `{{base_url}}/validate-report`

---

## Step 11: Batch Testing

### **Test Multiple Reports**

Create a sequence of requests to test different scenarios:

1. **Valid report with photo**
2. **Valid report without photo**
3. **Invalid coordinates**
4. **Missing fields**
5. **Check statistics after processing**

### **Automated Testing**

Use Postman's "Runner" feature:

1. **Open Runner:**
   - Click "Runner" in top bar

2. **Select Collection:**
   - Choose your "Community Mangrove Watch API" collection

3. **Configure:**
   - Environment: "Local Development"
   - Iterations: 1
   - Delay: 1000ms

4. **Run Tests:**
   - Click "Run Community Mangrove Watch API"

---

## Troubleshooting

### **Common Issues:**

1. **Connection Refused:**
   - Make sure API server is running
   - Check port 8000 is not in use

2. **Timeout Errors:**
   - Increase timeout in Postman settings
   - Check if satellite APIs are responding

3. **Validation Errors:**
   - Verify JSON format is correct
   - Check required fields are present

4. **500 Server Errors:**
   - Check API server logs
   - Verify all dependencies are installed

### **Debug Mode:**

Enable debug mode in your `.env` file:
```bash
API_DEBUG=true
```

This will show detailed error messages in responses.

---

## Success Criteria

✅ **All endpoints respond correctly**
✅ **Valid reports return proper validation results**
✅ **Error handling works for invalid inputs**
✅ **Statistics update after processing reports**
✅ **Health checks show healthy status**

---

## Next Steps

After successful Postman testing:

1. **Integrate with your web app**
2. **Add authentication if needed**
3. **Deploy to production**
4. **Monitor API performance**

Your API is now ready for production use! 🎉
