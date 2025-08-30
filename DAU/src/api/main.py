"""
FastAPI REST API for Community Mangrove Watch.
Provides endpoints for report validation and pipeline management.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
import traceback

from src.pipeline.mangrove_pipeline import MangrovePipeline
from src.utils.logger import log_api_request, setup_logger
from config.settings import settings

# Setup logging
setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Community Mangrove Watch API",
    description="AI-powered mangrove monitoring and validation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = MangrovePipeline()


# Pydantic models for request/response validation
class ReportRequest(BaseModel):
    """Request model for citizen reports."""
    photo_url: str = Field(..., description="URL of the geotagged photo (required)")
    timestamp: str = Field(..., description="ISO timestamp of the report")
    description: Optional[str] = Field("", description="Description of the incident")
    reporter_id: str = Field(..., description="Unique identifier for the reporter")
    
    # Note: latitude and longitude are now extracted from the geotagged photo
    # User-provided coordinates are ignored when photo is provided
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Use ISO format (e.g., 2024-01-15T10:30:00Z)')
    
    @validator('photo_url')
    def validate_photo_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must be a valid HTTP/HTTPS URL')
        return v


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    report_id: str
    reporter_id: str
    timestamp: str
    confidence_score: float
    confidence_level: str
    anomaly_detected: bool
    anomaly_score: float
    urgency_level: str
    citizen_confidence: float
    satellite_confidence: float
    inference_time: float
    summary: str
    recommendations: List[str]
    points_earned: int
    badges: List[str]
    processing_metadata: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    timestamp: str
    request_id: Optional[str] = None


class PipelineStatus(BaseModel):
    """Pipeline status response model."""
    status: str
    timestamp: str
    components: Dict[str, str]
    configuration: Dict[str, Any]
    model_info: Dict[str, str]


# Dependency for rate limiting (simplified)
def get_user_id(report: ReportRequest) -> str:
    """Extract user ID from request for rate limiting."""
    return report.reporter_id


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Community Mangrove Watch API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.post("/validate-report", response_model=ValidationResponse)
async def validate_report(
    report: ReportRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_user_id)
):
    """
    Validate a citizen report with AI-powered analysis.
    
    This endpoint processes citizen reports by:
    1. Preprocessing and validating the report data
    2. Fetching satellite imagery for the location
    3. Running AI validation using mangrove segmentation models
    4. Detecting anomalies and calculating confidence scores
    5. Generating recommendations and gamification rewards
    
    Args:
        report: Citizen report data with photo URL and location
        background_tasks: FastAPI background tasks
        user_id: User ID for rate limiting
        
    Returns:
        Validation results with confidence scores, anomaly detection, and recommendations
    """
    start_time = time.time()
    
    try:
        # Log API request
        log_api_request("/validate-report", "POST", user_id)
        
        # Validate input
        validation = pipeline.validate_input(report.dict())
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid input data",
                    "errors": validation['errors'],
                    "warnings": validation['warnings']
                }
            )
        
        # Process report through pipeline
        result = pipeline.process_report(report.dict())
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        log_api_request(
            "/validate-report", "POST", user_id, processing_time, 200
        )
        
        return ValidationResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Report validation failed: {str(e)}"
        
        # Log error
        log_api_request(
            "/validate-report", "POST", user_id, processing_time, 500, error_msg
        )
        
        # Return detailed error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback.format_exc() if settings.api.debug else None
            }
        )


@app.get("/status", response_model=PipelineStatus)
async def get_status():
    """
    Get pipeline status and health information.
    
    Returns:
        Current pipeline status, component health, and configuration
    """
    try:
        status = pipeline.get_pipeline_status()
        return PipelineStatus(**status)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get pipeline status",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/statistics")
async def get_statistics():
    """
    Get processing statistics and metrics.
    
    Returns:
        Processing statistics including success rates and activity metrics
    """
    try:
        stats = pipeline.get_processing_statistics()
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get statistics",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/test-connection")
async def test_connection():
    """
    Test API connectivity and basic functionality.
    
    Returns:
        Connection test results
    """
    try:
        # Test basic pipeline functionality
        test_report = {
            "latitude": 0.0,
            "longitude": 0.0,
            "timestamp": datetime.now().isoformat(),
            "description": "Test connection",
            "reporter_id": "test_user"
        }
        
        # Validate input (should pass)
        validation = pipeline.validate_input(test_report)
        
        return {
            "status": "connected",
            "pipeline_ready": validation['valid'],
            "timestamp": datetime.now().isoformat(),
            "message": "API is operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Connection test failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path,
            "traceback": traceback.format_exc() if settings.api.debug else None
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        status = pipeline.get_pipeline_status()
        return {
            "status": "healthy" if status['status'] == 'healthy' else 'degraded',
            "timestamp": datetime.now().isoformat(),
            "components": status['components']
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    try:
        # Test pipeline initialization
        status = pipeline.get_pipeline_status()
        if status['status'] == 'error':
            raise Exception("Pipeline initialization failed")
        
        print("Community Mangrove Watch API started successfully")
        print(f"Pipeline status: {status['status']}")
        
    except Exception as e:
        print(f"Failed to initialize API: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Community Mangrove Watch API shutting down...")


# Example usage and testing
if __name__ == "__main__":
    import uvicorn
    
    print("Starting Community Mangrove Watch API...")
    print(f"Host: {settings.api.host}")
    print(f"Port: {settings.api.port}")
    print(f"Debug: {settings.api.debug}")
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="info"
    )
