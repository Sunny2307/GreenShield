# Community Mangrove Watch - ML/DL Pipeline

A comprehensive machine learning and deep learning pipeline for participatory mangrove monitoring and conservation.

## Overview

This project implements an AI-powered validation system for citizen reports of mangrove incidents (illegal cutting, dumping, etc.). The pipeline processes geotagged photos from community members, validates them against satellite data, and provides confidence scores for authorities.

## Features

- **Report Preprocessing**: Parse and validate citizen reports with geotagged photos
- **Satellite Data Fetch**: Retrieve cloud-free Sentinel-2 imagery for validation
- **AI Validation**: Mangrove segmentation and anomaly detection using state-of-the-art models
- **REST API**: FastAPI endpoint for seamless integration with mobile apps
- **Gamification Ready**: Structured outputs for points and leaderboards

## Project Structure

```
├── src/
│   ├── preprocessing/          # Report preprocessing modules
│   ├── satellite/             # Satellite data fetching
│   ├── models/                # ML/DL models and validation
│   ├── api/                   # FastAPI endpoints
│   └── utils/                 # Utility functions
├── tests/                     # Unit tests
├── config/                    # Configuration files
├── models/                    # Pre-trained model weights
└── data/                      # Sample data and outputs
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the API**:
   ```bash
   python -m uvicorn src.api.main:app --reload
   ```

4. **Test the Pipeline**:
   ```bash
   python tests/test_pipeline.py
   ```

## API Endpoints

### POST /validate-report
Validates a citizen report with geotagged photo and location data.

**Request Body**:
```json
{
  "photo_url": "https://example.com/photo.jpg",
  "latitude": 12.3456,
  "longitude": 78.9012,
  "timestamp": "2024-01-15T10:30:00Z",
  "description": "Suspected illegal mangrove cutting",
  "reporter_id": "user123"
}
```

**Response**:
```json
{
  "confidence_score": 0.87,
  "anomaly_detected": true,
  "urgency_level": "high",
  "summary": "High confidence anomaly detected. Mangrove cover shows significant reduction compared to satellite baseline.",
  "segmentation_mask": "base64_encoded_mask",
  "processing_time": 2.34
}
```

## Model Architecture

The pipeline uses the Swin-UMamba model from [MangroveAI](https://github.com/lucasjvds/MangroveAI) for mangrove segmentation, achieving 72.87% IoU on Sentinel-2 imagery.

## Configuration

Key configuration parameters in `config/settings.py`:
- Satellite data source (Sentinel Hub vs Google Earth Engine)
- Model confidence thresholds
- Image preprocessing parameters
- API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [MangroveAI](https://github.com/lucasjvds/MangroveAI) for the segmentation models
- [OpenGeoAI](https://github.com/opengeos/geoai) for geospatial workflows
- Sentinel Hub and Google Earth Engine for satellite data access
