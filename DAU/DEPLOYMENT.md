# Community Mangrove Watch - Deployment Guide

This guide provides comprehensive instructions for deploying the Community Mangrove Watch ML pipeline in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [API Integration](#api-integration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: 10GB+ free space for models and data
- **GPU**: Optional but recommended for faster inference (NVIDIA GPU with CUDA support)

### Required Accounts and API Keys

1. **Sentinel Hub** (for satellite data):
   - Sign up at [https://apps.sentinel-hub.com/](https://apps.sentinel-hub.com/)
   - Create a new OAuth client
   - Note your Client ID and Client Secret

2. **Google Earth Engine** (alternative satellite data source):
   - Sign up at [https://earthengine.google.com/](https://earthengine.google.com/)
   - Enable the Earth Engine API
   - Set up service account credentials

3. **Model Weights** (optional):
   - Download pre-trained Swin-UMamba weights from [MangroveAI](https://github.com/lucasjvds/MangroveAI)
   - Place in `models/` directory

## Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mangrove-watch

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```bash
# Satellite Data APIs
SENTINEL_HUB_CLIENT_ID=your_client_id
SENTINEL_HUB_CLIENT_SECRET=your_client_secret

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

### 3. Initialize Models

```bash
# Create model directories
mkdir -p models logs data

# Download pre-trained models (if available)
# Place model files in models/ directory
```

### 4. Run the API

```bash
# Start the FastAPI server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the Setup

```bash
# Run tests
python -m pytest tests/

# Run integration examples
python examples/integration_example.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## Production Deployment

### 1. Production Environment Setup

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Create production user
sudo useradd -m -s /bin/bash mangrove
sudo usermod -aG sudo mangrove
```

### 2. Application Setup

```bash
# Switch to production user
sudo su - mangrove

# Clone application
git clone <repository-url> /home/mangrove/mangrove-watch
cd /home/mangrove/mangrove-watch

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with production settings
```

### 3. Systemd Service Configuration

Create `/etc/systemd/system/mangrove-watch.service`:

```ini
[Unit]
Description=Community Mangrove Watch API
After=network.target

[Service]
Type=exec
User=mangrove
Group=mangrove
WorkingDirectory=/home/mangrove/mangrove-watch
Environment=PATH=/home/mangrove/mangrove-watch/venv/bin
ExecStart=/home/mangrove/mangrove-watch/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/mangrove-watch`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/mangrove/mangrove-watch/static/;
    }
}
```

### 5. Start Services

```bash
# Enable and start services
sudo systemctl enable mangrove-watch
sudo systemctl start mangrove-watch
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status mangrove-watch
sudo systemctl status nginx
```

## Docker Deployment

### 1. Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mangrove-watch:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SENTINEL_HUB_CLIENT_ID=${SENTINEL_HUB_CLIENT_ID}
      - SENTINEL_HUB_CLIENT_SECRET=${SENTINEL_HUB_CLIENT_SECRET}
      - API_DEBUG=false
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mangrove-watch
    restart: unless-stopped
```

### 3. Build and Run

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f mangrove-watch

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Setup

```bash
# Launch EC2 instance (t3.large or larger recommended)
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx git

# Clone and setup application
git clone <repository-url>
cd mangrove-watch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. AWS Lambda Deployment (Alternative)

Create `lambda_function.py`:

```python
import json
from src.pipeline.mangrove_pipeline import MangrovePipeline

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body'])
        
        # Initialize pipeline
        pipeline = MangrovePipeline()
        
        # Process report
        result = pipeline.process_report(body)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Google Cloud Platform Deployment

#### 1. App Engine Deployment

Create `app.yaml`:

```yaml
runtime: python39
entrypoint: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT

env_variables:
  SENTINEL_HUB_CLIENT_ID: "your_client_id"
  SENTINEL_HUB_CLIENT_SECRET: "your_client_secret"
  API_DEBUG: "false"

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
```

Deploy:
```bash
gcloud app deploy
```

## API Integration

### 1. Mobile App Integration

```python
# Example Python client
import requests

class MangroveWatchClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def submit_report(self, photo_url, latitude, longitude, description, user_id):
        data = {
            "photo_url": photo_url,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "reporter_id": user_id
        }
        
        response = requests.post(f"{self.base_url}/validate-report", json=data)
        return response.json()
```

### 2. Web Dashboard Integration

```javascript
// Example JavaScript client
class MangroveWatchAPI {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }
    
    async submitReport(reportData) {
        const response = await fetch(`${this.baseURL}/validate-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reportData)
        });
        
        return await response.json();
    }
    
    async getStatistics() {
        const response = await fetch(`${this.baseURL}/statistics`);
        return await response.json();
    }
}
```

### 3. Webhook Integration

```python
# Example webhook handler
@app.post("/webhook/mangrove-report")
async def handle_webhook(request: Request):
    data = await request.json()
    
    # Process the report
    pipeline = MangrovePipeline()
    result = pipeline.process_report(data)
    
    # Send notifications based on urgency
    if result['urgency_level'] in ['high', 'critical']:
        await send_alert_notification(result)
    
    return {"status": "processed"}
```

## Monitoring and Maintenance

### 1. Logging Configuration

```python
# Enhanced logging configuration
import logging
from loguru import logger

# Configure structured logging
logger.add(
    "logs/mangrove_watch.json",
    format="{time} | {level} | {message}",
    serialize=True,
    rotation="100 MB",
    retention="30 days"
)
```

### 2. Health Monitoring

```bash
# Create monitoring script
cat > /usr/local/bin/mangrove-monitor.sh << 'EOF'
#!/bin/bash

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ $response -ne 200 ]; then
    echo "Mangrove Watch API is down!"
    # Send alert
    curl -X POST -H "Content-Type: application/json" \
         -d '{"text":"Mangrove Watch API is down!"}' \
         https://hooks.slack.com/services/YOUR_WEBHOOK_URL
fi
EOF

chmod +x /usr/local/bin/mangrove-monitor.sh

# Add to crontab
echo "*/5 * * * * /usr/local/bin/mangrove-monitor.sh" | crontab -
```

### 3. Performance Monitoring

```python
# Add performance metrics
import time
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
REPORT_COUNTER = Counter('reports_processed_total', 'Total reports processed')
PROCESSING_TIME = Histogram('report_processing_seconds', 'Report processing time')
ERROR_COUNTER = Counter('report_errors_total', 'Total processing errors')

# In your API endpoint
@app.post("/validate-report")
async def validate_report(report: ReportRequest):
    start_time = time.time()
    
    try:
        result = pipeline.process_report(report.dict())
        REPORT_COUNTER.inc()
        PROCESSING_TIME.observe(time.time() - start_time)
        return result
    except Exception as e:
        ERROR_COUNTER.inc()
        raise
```

## Troubleshooting

### Common Issues

#### 1. Satellite Data Fetch Failures

```bash
# Check API credentials
echo $SENTINEL_HUB_CLIENT_ID
echo $SENTINEL_HUB_CLIENT_SECRET

# Test API connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://services.sentinel-hub.com/oauth/token"
```

#### 2. Model Loading Issues

```bash
# Check model files
ls -la models/

# Verify model paths in configuration
grep -r "model_path" config/
```

#### 3. Memory Issues

```bash
# Monitor memory usage
htop
free -h

# Check for memory leaks
python -m memory_profiler src/api/main.py
```

#### 4. API Performance Issues

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/health"

# Monitor system resources
iostat -x 1
```

### Debug Mode

```bash
# Enable debug logging
export API_DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
python -m uvicorn src.api.main:app --reload --log-level debug
```

### Support and Resources

- **Documentation**: [API Documentation](http://localhost:8000/docs)
- **Issues**: GitHub Issues page
- **Community**: Join our Discord/Slack channel
- **Email**: support@mangrovewatch.org

## Security Considerations

### 1. API Security

```python
# Add authentication middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify token logic here
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token
```

### 2. Rate Limiting

```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/validate-report")
@limiter.limit("10/minute")
async def validate_report(request: Request, report: ReportRequest):
    # Your endpoint logic
    pass
```

### 3. Input Validation

```python
# Enhanced input validation
from pydantic import validator, Field

class ReportRequest(BaseModel):
    photo_url: Optional[str] = Field(None, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    description: str = Field(..., min_length=10, max_length=1000)
    reporter_id: str = Field(..., min_length=3, max_length=50)
    
    @validator('photo_url')
    def validate_photo_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must be a valid HTTP/HTTPS URL')
        return v
```

This deployment guide provides comprehensive instructions for setting up the Community Mangrove Watch ML pipeline in various environments. Follow the sections relevant to your deployment needs and refer to the troubleshooting section if you encounter issues.
