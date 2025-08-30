"""
Configuration settings for the Community Mangrove Watch ML pipeline.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SatelliteConfig:
    """Configuration for satellite data sources."""
    # Sentinel Hub configuration
    sentinel_hub_client_id: str = os.getenv("SENTINEL_HUB_CLIENT_ID", "")
    sentinel_hub_client_secret: str = os.getenv("SENTINEL_HUB_CLIENT_SECRET", "")
    
    # Google Earth Engine configuration
    earth_engine_service_account: str = os.getenv("EARTH_ENGINE_SERVICE_ACCOUNT", "")
    earth_engine_private_key: str = os.getenv("EARTH_ENGINE_PRIVATE_KEY", "")
    
    # Default satellite data source
    default_source: str = "sentinel_hub"  # or "earth_engine"
    
    # Image parameters
    image_size: int = 512
    cloud_coverage_threshold: float = 0.1
    date_range_days: int = 30

@dataclass
class ModelConfig:
    """Configuration for ML/DL models."""
    # Model paths
    mangrove_segmentation_model_path: str = "models/swin_umamba_mangrove.pth"
    anomaly_detection_model_path: str = "models/anomaly_detector.pkl"
    
    # Model parameters
    confidence_threshold: float = 0.7
    anomaly_threshold: float = 0.8
    segmentation_threshold: float = 0.5
    
    # Image preprocessing
    input_size: int = 512
    normalize_mean: tuple = (0.485, 0.456, 0.406)
    normalize_std: tuple = (0.229, 0.224, 0.225)

@dataclass
class APIConfig:
    """Configuration for the REST API."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 60

@dataclass
class ProcessingConfig:
    """Configuration for data processing."""
    # Image processing
    max_image_size: int = 2048
    supported_formats: tuple = ('.jpg', '.jpeg', '.png', '.tiff')
    
    # Coordinate validation
    max_coordinate_error: float = 0.001  # degrees
    min_photo_quality: float = 0.3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/mangrove_pipeline.log"

@dataclass
class GamificationConfig:
    """Configuration for gamification features."""
    # Points system
    base_points_per_report: int = 10
    bonus_points_high_confidence: int = 5
    bonus_points_anomaly_detected: int = 15
    
    # Confidence thresholds for points
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.6
    
    # Urgency levels
    urgency_levels: Dict[str, int] = None
    
    def __post_init__(self):
        if self.urgency_levels is None:
            self.urgency_levels = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "critical": 4
            }

class Settings:
    """Main settings class that combines all configurations."""
    
    def __init__(self):
        self.satellite = SatelliteConfig()
        self.model = ModelConfig()
        self.api = APIConfig()
        self.processing = ProcessingConfig()
        self.gamification = GamificationConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for API responses."""
        return {
            "satellite": self.satellite.__dict__,
            "model": self.model.__dict__,
            "api": self.api.__dict__,
            "processing": self.processing.__dict__,
            "gamification": self.gamification.__dict__
        }

# Global settings instance
settings = Settings()
