"""
Logging utilities for the Community Mangrove Watch ML pipeline.
"""
import os
import sys
from datetime import datetime
from loguru import logger
from typing import Optional

def setup_logger(
    log_file: str = "logs/mangrove_pipeline.log",
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "30 days"
) -> None:
    """
    Setup logger configuration for the pipeline.
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: Log rotation size
        retention: Log retention period
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file logger
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip"
    )

def log_report_processing(
    report_id: str,
    reporter_id: str,
    latitude: float,
    longitude: float,
    processing_time: float,
    confidence_score: float,
    anomaly_detected: bool,
    error: Optional[str] = None
) -> None:
    """
    Log report processing results.
    
    Args:
        report_id: Unique identifier for the report
        reporter_id: ID of the person who submitted the report
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        processing_time: Time taken to process the report
        confidence_score: AI confidence score
        anomaly_detected: Whether an anomaly was detected
        error: Error message if processing failed
    """
    if error:
        logger.error(
            f"Report processing failed | Report ID: {report_id} | "
            f"Reporter: {reporter_id} | Location: ({latitude:.6f}, {longitude:.6f}) | "
            f"Error: {error}"
        )
    else:
        logger.info(
            f"Report processed successfully | Report ID: {report_id} | "
            f"Reporter: {reporter_id} | Location: ({latitude:.6f}, {longitude:.6f}) | "
            f"Processing time: {processing_time:.2f}s | "
            f"Confidence: {confidence_score:.3f} | "
            f"Anomaly: {anomaly_detected}"
        )

def log_satellite_data_fetch(
    latitude: float,
    longitude: float,
    date_range: str,
    data_source: str,
    success: bool,
    error: Optional[str] = None
) -> None:
    """
    Log satellite data fetching operations.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        date_range: Date range for data fetch
        data_source: Source of satellite data (sentinel_hub, earth_engine)
        success: Whether the fetch was successful
        error: Error message if fetch failed
    """
    if error:
        logger.error(
            f"Satellite data fetch failed | Location: ({latitude:.6f}, {longitude:.6f}) | "
            f"Date range: {date_range} | Source: {data_source} | Error: {error}"
        )
    else:
        logger.info(
            f"Satellite data fetched successfully | Location: ({latitude:.6f}, {longitude:.6f}) | "
            f"Date range: {date_range} | Source: {data_source}"
        )

def log_model_inference(
    model_name: str,
    input_size: tuple,
    inference_time: float,
    confidence_score: float,
    error: Optional[str] = None
) -> None:
    """
    Log model inference operations.
    
    Args:
        model_name: Name of the model used
        input_size: Size of input image
        inference_time: Time taken for inference
        confidence_score: Model confidence score
        error: Error message if inference failed
    """
    if error:
        logger.error(
            f"Model inference failed | Model: {model_name} | "
            f"Input size: {input_size} | Error: {error}"
        )
    else:
        logger.info(
            f"Model inference completed | Model: {model_name} | "
            f"Input size: {input_size} | Inference time: {inference_time:.3f}s | "
            f"Confidence: {confidence_score:.3f}"
        )

def log_api_request(
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    processing_time: Optional[float] = None,
    status_code: int = 200,
    error: Optional[str] = None
) -> None:
    """
    Log API request details.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        user_id: ID of the user making the request
        processing_time: Time taken to process the request
        status_code: HTTP status code
        error: Error message if request failed
    """
    if error:
        logger.error(
            f"API request failed | {method} {endpoint} | "
            f"User: {user_id} | Status: {status_code} | Error: {error}"
        )
    else:
        logger.info(
            f"API request completed | {method} {endpoint} | "
            f"User: {user_id} | Status: {status_code}" + 
            (f" | Processing time: {processing_time:.3f}s" if processing_time is not None else "")
        )

# Initialize logger with default settings
setup_logger()
