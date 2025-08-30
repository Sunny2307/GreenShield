# Local Setup Guide - Community Mangrove Watch

This guide shows you how to run the ML/DL pipeline locally without Docker.

## Quick Start (No Docker Required)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv mangrove_env
source mangrove_env/bin/activate  # On Windows: mangrove_env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your settings (optional for testing):
```bash
# For testing, you can leave these empty
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=
EARTH_ENGINE_CREDENTIALS=

# API settings
API_HOST=localhost
API_PORT=8000
API_DEBUG=true
```

### 3. Run the API Server

```bash
# Start the FastAPI server
python -m uvicorn src.api.main:app --host localhost --port 8000 --reload
```

The API will be available at: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Data Flow and Formats

### 1. Input Format (User Submits Report)

**JSON Request to `/validate-report`:**

```json
{
  "photo_url": "https://example.com/mangrove_photo.jpg",
  "latitude": 12.345678,
  "longitude": 78.901234,
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Suspicious mangrove cutting activity",
  "reporter_id": "user123"
}
```

**Field Descriptions:**
- `photo_url` (optional): URL of geotagged photo
- `latitude` (required): GPS latitude (-90 to 90)
- `longitude` (required): GPS longitude (-180 to 180)
- `timestamp` (required): ISO format timestamp
- `description` (optional): Text description of incident
- `reporter_id` (required): Unique user identifier

### 2. Pipeline Processing Flow

```
User Report → Preprocessing → Satellite Data → AI Validation → Postprocessing → Response
```

**Step 1: Preprocessing**
- Validates coordinates and timestamp
- Downloads and processes photo (resize to 512x512, normalize)
- Calculates image quality score
- Extracts metadata

**Step 2: Satellite Data**
- Fetches Sentinel-2 imagery for location
- Filters for cloud-free images (< 10% clouds)
- Calculates NDVI (vegetation index)
- Returns RGB + NIR bands

**Step 3: AI Validation**
- Runs Swin-UMamba segmentation on citizen photo
- Runs segmentation on satellite image
- Compares results for inconsistencies
- Uses Isolation Forest for anomaly detection
- Calculates confidence scores

**Step 4: Postprocessing**
- Determines confidence level (Low/Medium/High)
- Determines urgency level (Low/Medium/High/Critical)
- Generates human-readable summary
- Calculates gamification points and badges

### 3. Output Format (API Response)

**JSON Response from `/validate-report`:**

```json
{
  "report_id": "report_20240115_103000_user123",
  "reporter_id": "user123",
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

## Testing the System

### 1. Test with Python Client

```python
import requests
import json
from datetime import datetime

# Test report
report = {
    "photo_url": "https://example.com/mangrove_photo.jpg",
    "latitude": 12.345678,
    "longitude": 78.901234,
    "timestamp": datetime.now().isoformat(),
    "description": "Test mangrove report",
    "reporter_id": "test_user"
}

# Submit to API
response = requests.post(
    "http://localhost:8000/validate-report",
    json=report
)

result = response.json()
print(json.dumps(result, indent=2))
```

### 2. Run Integration Examples

```bash
# Run the complete example suite
python examples/integration_example.py
```

### 3. Test Individual Components

```python
# Test preprocessing only
from src.preprocessing.report_processor import ReportProcessor
processor = ReportProcessor()
result = processor.parse_report_json(report_data)

# Test satellite data fetching
from src.satellite.data_fetcher import SatelliteDataFetcher
fetcher = SatelliteDataFetcher()
satellite_data = fetcher.fetch_sentinel2_image(12.345, 78.901)

# Test AI validation
from src.models.mangrove_validator import MangroveValidator
validator = MangroveValidator()
validation = validator.validate_report(photo, satellite_image, (12.345, 78.901))
```

## API Endpoints

### Main Endpoint
- **POST** `/validate-report` - Submit citizen report for validation

### Utility Endpoints
- **GET** `/` - API information
- **GET** `/health` - Health check
- **GET** `/status` - Pipeline status
- **GET** `/statistics` - Processing statistics
- **POST** `/test-connection` - Test connectivity

### Interactive Documentation
- **GET** `/docs` - Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation

## Error Handling

The API returns structured error responses:

```json
{
  "error": "Invalid input data",
  "message": "Validation failed",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": {
    "errors": ["Invalid latitude: 100.0"],
    "warnings": ["Photo URL not provided"]
  }
}
```

## Performance

- **Processing Time**: 2-5 seconds per report
- **Concurrent Requests**: Supports multiple simultaneous reports
- **Memory Usage**: ~2GB RAM for full pipeline
- **Storage**: Minimal (logs and temporary files only)

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use different port
   python -m uvicorn src.api.main:app --port 8001
   ```

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Model files not found**
   ```bash
   # Create models directory
   mkdir -p models
   # Models will be downloaded automatically on first use
   ```

4. **Satellite API errors**
   - Check internet connection
   - Verify API credentials in `.env`
   - For testing, the system works without satellite data

### Logs

Check logs in `logs/mangrove_pipeline.log` for detailed information.

## Next Steps

1. **Customize Models**: Modify `src/models/mangrove_validator.py` for your specific needs
2. **Add Authentication**: Implement user authentication in `src/api/main.py`
3. **Scale Up**: Deploy to cloud services (see `DEPLOYMENT.md`)
4. **Integrate with Web App**: Use the API endpoints in your mobile/web application

The system is now ready for local development and testing!
