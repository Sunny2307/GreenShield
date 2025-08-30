"""
Report preprocessing module for Community Mangrove Watch.
Handles parsing, validation, and preprocessing of citizen reports.
"""
import json
import uuid
import requests
import cv2
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import io
import os
from loguru import logger

from config.settings import settings
from src.utils.logger import log_report_processing
from src.preprocessing.photo_processor import PhotoProcessor


class ReportProcessor:
    """
    Processes and validates citizen reports with geotagged photos.
    """
    
    def __init__(self):
        self.supported_formats = settings.processing.supported_formats
        self.max_image_size = settings.processing.max_image_size
        self.max_coordinate_error = settings.processing.max_coordinate_error
        self.min_photo_quality = settings.processing.min_photo_quality
        self.photo_processor = PhotoProcessor()
    
    def parse_report_json(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate a citizen report JSON.
        
        Args:
            report_data: Raw report data from citizen
            
        Returns:
            Structured dictionary with validated and processed data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Generate unique report ID
            report_id = str(uuid.uuid4())
            
            # Extract and validate required fields (latitude/longitude now extracted from photos)
            required_fields = ['photo_url', 'timestamp', 'reporter_id']
            for field in required_fields:
                if field not in report_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Initialize coordinates (will be extracted from photo)
            latitude = None
            longitude = None
            
            # Validate timestamp
            timestamp = self._parse_timestamp(report_data['timestamp'])
            
            # Extract optional fields
            photo_url = report_data.get('photo_url', '')
            description = report_data.get('description', '')
            reporter_id = report_data['reporter_id']
            
            # Process photo if provided
            photo_data = None
            extracted_latitude = None
            extracted_longitude = None
            
            if photo_url:
                try:
                    # Process geotagged photo and extract coordinates
                    photo_data = self.photo_processor.process_geotagged_photo(photo_url)
                    extracted_latitude = photo_data['gps_coordinates']['latitude']
                    extracted_longitude = photo_data['gps_coordinates']['longitude']
                    
                    # Use extracted coordinates instead of user-provided ones
                    latitude = extracted_latitude
                    longitude = extracted_longitude
                    
                    logger.info(f"Using GPS coordinates from photo: ({latitude}, {longitude})")
                    
                except ValueError as e:
                    # If photo processing fails, raise error
                    raise ValueError(f"Photo processing failed: {str(e)}")
            else:
                # No photo provided, use user coordinates
                logger.info(f"Using user-provided coordinates: ({latitude}, {longitude})")
            
            # Create structured report
            structured_report = {
                'report_id': report_id,
                'reporter_id': reporter_id,
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp,
                'description': description,
                'photo_url': photo_url,
                'photo_data': photo_data,
                'metadata': {
                    'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                    'photo_processed': photo_data is not None,
                    'photo_quality_score': photo_data['quality_score'] if photo_data else None,
                    'original_image_size': photo_data['original_size'] if photo_data else None,
                    'processed_image_size': photo_data['processed_size'] if photo_data else None,
                    'coordinates_source': 'photo_gps' if extracted_latitude else 'user_input',
                    'extracted_coordinates': {
                        'latitude': extracted_latitude,
                        'longitude': extracted_longitude
                    } if extracted_latitude else None
                }
            }
            
            logger.info(f"Report parsed successfully: {report_id}")
            return structured_report
            
        except Exception as e:
            logger.error(f"Failed to parse report: {str(e)}")
            raise ValueError(f"Report parsing failed: {str(e)}")
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Raises:
            ValueError: If coordinates are invalid
        """
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
        
        # Check for exactly zero coordinates (likely invalid)
        if latitude == 0.0 and longitude == 0.0:
            raise ValueError(f"Coordinates too close to zero: ({latitude}, {longitude})")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse and validate timestamp string.
        
        Args:
            timestamp_str: Timestamp string in ISO format
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If timestamp is invalid
        """
        try:
            # Try parsing ISO format
            if 'T' in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S']:
                    try:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(f"Unsupported timestamp format: {timestamp_str}")
            
            # Ensure timezone awareness
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Validate timestamp is not in the future
            if timestamp > datetime.now(timezone.utc):
                raise ValueError(f"Timestamp is in the future: {timestamp}")
            
            return timestamp
            
        except Exception as e:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}. Error: {str(e)}")
    
    def _process_photo(self, photo_url: str) -> Optional[Dict[str, Any]]:
        """
        Download, validate, and preprocess photo from URL.
        
        Args:
            photo_url: URL of the photo to process
            
        Returns:
            Dictionary containing processed photo data or None if processing fails
        """
        try:
            # Download photo
            response = requests.get(photo_url, timeout=30)
            response.raise_for_status()
            
            # Validate file format
            file_extension = os.path.splitext(photo_url)[1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Load image
            image = Image.open(io.BytesIO(response.content))
            original_size = image.size
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Calculate quality score
            quality_score = self._calculate_photo_quality(image)
            
            if quality_score < self.min_photo_quality:
                logger.warning(f"Photo quality too low: {quality_score:.3f}")
                return None
            
            # Resize if too large
            if max(image.size) > self.max_image_size:
                image = self._resize_image(image, self.max_image_size)
            
            # Normalize image
            normalized_image = self._normalize_image(image)
            
            # Convert to numpy array
            image_array = np.array(normalized_image)
            
            return {
                'image_array': image_array,
                'original_size': original_size,
                'processed_size': image.size,
                'quality_score': quality_score,
                'file_size': len(response.content),
                'format': file_extension
            }
            
        except Exception as e:
            logger.error(f"Failed to process photo from {photo_url}: {str(e)}")
            return None
    
    def _calculate_photo_quality(self, image: Image.Image) -> float:
        """
        Calculate photo quality score based on various metrics.
        
        Args:
            image: PIL Image object
            
        Returns:
            Quality score between 0 and 1
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate blur score using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize blur score (higher is better)
            blur_score = min(blur_score / 1000, 1.0)
            
            # Calculate brightness score
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            
            # Calculate contrast score
            contrast = np.std(gray)
            contrast_score = min(contrast / 50, 1.0)
            
            # Combine scores
            quality_score = (blur_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Failed to calculate photo quality: {str(e)}")
            return 0.5  # Default score
    
    def _resize_image(self, image: Image.Image, max_size: int) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: PIL Image object
            max_size: Maximum dimension size
            
        Returns:
            Resized image
        """
        width, height = image.size
        
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _normalize_image(self, image: Image.Image) -> Image.Image:
        """
        Normalize image for model input.
        
        Args:
            image: PIL Image object
            
        Returns:
            Normalized image
        """
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1] range
        img_array = img_array / 255.0
        
        # Apply ImageNet normalization
        mean = np.array(settings.model.normalize_mean)
        std = np.array(settings.model.normalize_std)
        
        img_array = (img_array - mean) / std
        
        # Convert back to PIL Image
        img_array = np.clip(img_array, 0, 1)
        img_array = (img_array * 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def validate_report_quality(self, structured_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate overall report quality and add quality metrics.
        
        Args:
            structured_report: Structured report data
            
        Returns:
            Report with quality validation results
        """
        quality_metrics = {
            'has_photo': structured_report['photo_data'] is not None,
            'photo_quality': structured_report['metadata']['photo_quality_score'],
            'coordinate_accuracy': self._assess_coordinate_accuracy(
                structured_report['latitude'], 
                structured_report['longitude']
            ),
            'description_length': len(structured_report['description']),
            'timestamp_recency': self._assess_timestamp_recency(
                structured_report['timestamp']
            )
        }
        
        # Calculate overall quality score
        quality_score = self._calculate_overall_quality(quality_metrics)
        quality_metrics['overall_quality_score'] = quality_score
        
        # Add quality metrics to report
        structured_report['quality_metrics'] = quality_metrics
        
        return structured_report
    
    def _assess_coordinate_accuracy(self, latitude: float, longitude: float) -> float:
        """
        Assess coordinate accuracy based on precision and location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Accuracy score between 0 and 1
        """
        # Check decimal places (more decimal places = higher precision)
        lat_precision = len(str(latitude).split('.')[-1]) if '.' in str(latitude) else 0
        lon_precision = len(str(longitude).split('.')[-1]) if '.' in str(longitude) else 0
        
        precision_score = min((lat_precision + lon_precision) / 12, 1.0)
        
        # Check if coordinates are in reasonable ranges for mangroves
        # Mangroves typically grow in tropical and subtropical coastal areas
        lat_score = 1.0 if -30 <= latitude <= 30 else 0.5
        lon_score = 1.0 if -180 <= longitude <= 180 else 0.0
        
        return (precision_score * 0.6 + lat_score * 0.2 + lon_score * 0.2)
    
    def _assess_timestamp_recency(self, timestamp: datetime) -> float:
        """
        Assess timestamp recency.
        
        Args:
            timestamp: Report timestamp
            
        Returns:
            Recency score between 0 and 1
        """
        now = datetime.now(timezone.utc)
        time_diff = now - timestamp
        
        # Score based on how recent the report is (within 24 hours = 1.0, older = lower)
        hours_diff = time_diff.total_seconds() / 3600
        recency_score = max(0.0, 1.0 - (hours_diff / 24))
        
        return recency_score
    
    def _calculate_overall_quality(self, quality_metrics: Dict[str, Any]) -> float:
        """
        Calculate overall report quality score.
        
        Args:
            quality_metrics: Individual quality metrics
            
        Returns:
            Overall quality score between 0 and 1
        """
        weights = {
            'has_photo': 0.3,
            'photo_quality': 0.25,
            'coordinate_accuracy': 0.2,
            'description_length': 0.15,
            'timestamp_recency': 0.1
        }
        
        scores = {
            'has_photo': 1.0 if quality_metrics['has_photo'] else 0.0,
            'photo_quality': quality_metrics['photo_quality'] or 0.0,
            'coordinate_accuracy': quality_metrics['coordinate_accuracy'],
            'description_length': min(quality_metrics['description_length'] / 100, 1.0),
            'timestamp_recency': quality_metrics['timestamp_recency']
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights)
        return overall_score


# Example usage and testing
if __name__ == "__main__":
    # Test the report processor
    processor = ReportProcessor()
    
    # Sample report data
    sample_report = {
        "photo_url": "https://example.com/mangrove_photo.jpg",
        "latitude": 12.345678,
        "longitude": 78.901234,
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Suspected illegal mangrove cutting in the area",
        "reporter_id": "user123"
    }
    
    try:
        # Parse and validate report
        structured_report = processor.parse_report_json(sample_report)
        
        # Validate quality
        final_report = processor.validate_report_quality(structured_report)
        
        print("Report processed successfully!")
        print(f"Report ID: {final_report['report_id']}")
        print(f"Quality Score: {final_report['quality_metrics']['overall_quality_score']:.3f}")
        
    except ValueError as e:
        print(f"Report processing failed: {e}")
