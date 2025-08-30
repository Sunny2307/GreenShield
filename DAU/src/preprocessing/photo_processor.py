#!/usr/bin/env python3
"""
Photo processing module for extracting GPS coordinates from geotagged photos.
Handles EXIF data extraction and coordinate validation.
"""

import os
import io
import requests
import cv2
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
import piexif
from loguru import logger

from config.settings import settings


class PhotoProcessor:
    """
    Processes geotagged photos and extracts GPS coordinates.
    """
    
    def __init__(self):
        self.supported_formats = settings.processing.supported_formats
        self.max_image_size = settings.processing.max_image_size
        self.min_photo_quality = settings.processing.min_photo_quality
    
    def process_geotagged_photo(self, photo_url: str) -> Dict[str, Any]:
        """
        Process a geotagged photo and extract GPS coordinates.
        
        Args:
            photo_url: URL of the geotagged photo
            
        Returns:
            Dictionary containing processed photo data and GPS coordinates
            
        Raises:
            ValueError: If photo is not geotagged or format is invalid
        """
        try:
            # Download and validate photo
            photo_data = self._download_photo(photo_url)
            
            # Extract GPS coordinates
            gps_coords = self._extract_gps_coordinates(photo_data['image'])
            
            if gps_coords is None:
                raise ValueError("Photo is not geotagged. Please upload a photo with GPS coordinates.")
            
            # Process image for AI analysis
            processed_image = self._process_image_for_ai(photo_data['image'])
            
            # Calculate quality score
            quality_score = self._calculate_photo_quality(photo_data['image'])
            
            if quality_score < self.min_photo_quality:
                logger.warning(f"Photo quality too low: {quality_score:.3f}")
                raise ValueError(f"Photo quality too low ({quality_score:.3f}). Please upload a clearer photo.")
            
            return {
                'image_array': processed_image,
                'original_size': photo_data['original_size'],
                'processed_size': photo_data['processed_size'],
                'quality_score': quality_score,
                'file_size': photo_data['file_size'],
                'format': photo_data['format'],
                'gps_coordinates': {
                    'latitude': gps_coords[0],
                    'longitude': gps_coords[1],
                    'extraction_method': 'exif_gps'
                },
                'exif_data': photo_data.get('exif_data', {}),
                'is_geotagged': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process geotagged photo from {photo_url}: {str(e)}")
            raise
    
    def _download_photo(self, photo_url: str) -> Dict[str, Any]:
        """
        Download photo from URL and validate format.
        
        Args:
            photo_url: URL of the photo
            
        Returns:
            Dictionary containing image data and metadata
        """
        try:
            # Download photo
            response = requests.get(photo_url, timeout=30)
            response.raise_for_status()
            
            # Validate file format
            file_extension = os.path.splitext(photo_url)[1].lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: {', '.join(self.supported_formats)}")
            
            # Load image
            image = Image.open(io.BytesIO(response.content))
            original_size = image.size
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract EXIF data
            exif_data = self._extract_exif_data(image)
            
            # Resize if too large
            if max(image.size) > self.max_image_size:
                image = self._resize_image(image, self.max_image_size)
            
            return {
                'image': image,
                'original_size': original_size,
                'processed_size': image.size,
                'file_size': len(response.content),
                'format': file_extension,
                'exif_data': exif_data
            }
            
        except Exception as e:
            raise ValueError(f"Failed to download photo: {str(e)}")
    
    def _extract_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract EXIF data from image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary containing EXIF data
        """
        exif_data = {}
        
        try:
            # Get EXIF data
            exif = image._getexif()
            if exif is None:
                return exif_data
            
            # Convert EXIF tags to readable names
            for tag_id in exif:
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                data = exif.get(tag_id)
                exif_data[tag] = data
            
            # Extract GPS info specifically
            gps_info = exif_data.get('GPSInfo', {})
            if gps_info:
                exif_data['GPSInfo'] = gps_info
                
        except Exception as e:
            logger.warning(f"Failed to extract EXIF data: {str(e)}")
        
        return exif_data
    
    def _extract_gps_coordinates(self, image: Image.Image) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from image EXIF data.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (latitude, longitude) or None if not geotagged
        """
        try:
            # Get EXIF data
            exif = image._getexif()
            if exif is None:
                return None
            
            # Find GPS info
            gps_info = exif.get(ExifTags.TAGS.get('GPSInfo', 'GPSInfo'))
            if gps_info is None:
                return None
            
            # Extract latitude and longitude
            latitude = self._convert_to_degrees(gps_info.get(2, []))  # GPSLatitude
            longitude = self._convert_to_degrees(gps_info.get(4, []))  # GPSLongitude
            
            # Check latitude reference (N/S)
            lat_ref = gps_info.get(1, 'N')  # GPSLatitudeRef
            if lat_ref == 'S':
                latitude = -latitude
            
            # Check longitude reference (E/W)
            lon_ref = gps_info.get(3, 'E')  # GPSLongitudeRef
            if lon_ref == 'W':
                longitude = -longitude
            
            # Validate coordinates
            if latitude is None or longitude is None:
                return None
            
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                logger.warning(f"Invalid GPS coordinates: ({latitude}, {longitude})")
                return None
            
            logger.info(f"Extracted GPS coordinates: ({latitude}, {longitude})")
            return (latitude, longitude)
            
        except Exception as e:
            logger.warning(f"Failed to extract GPS coordinates: {str(e)}")
            return None
    
    def _convert_to_degrees(self, gps_coords: list) -> Optional[float]:
        """
        Convert GPS coordinates from degrees/minutes/seconds to decimal degrees.
        
        Args:
            gps_coords: List of [degrees, minutes, seconds]
            
        Returns:
            Decimal degrees or None if conversion fails
        """
        try:
            if len(gps_coords) != 3:
                return None
            
            degrees = float(gps_coords[0])
            minutes = float(gps_coords[1])
            seconds = float(gps_coords[2])
            
            decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
            return decimal_degrees
            
        except (ValueError, TypeError, IndexError):
            return None
    
    def _process_image_for_ai(self, image: Image.Image) -> np.ndarray:
        """
        Process image for AI model input.
        
        Args:
            image: PIL Image object
            
        Returns:
            Processed numpy array
        """
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1] range
        img_array = img_array / 255.0
        
        # Apply ImageNet normalization
        mean = np.array(settings.model.normalize_mean)
        std = np.array(settings.model.normalize_std)
        
        img_array = (img_array - mean) / std
        
        return img_array
    
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
    
    def validate_photo_format(self, photo_url: str) -> bool:
        """
        Validate if photo format is supported.
        
        Args:
            photo_url: URL of the photo
            
        Returns:
            True if format is supported, False otherwise
        """
        file_extension = os.path.splitext(photo_url)[1].lower()
        return file_extension in self.supported_formats
    
    def is_geotagged(self, photo_url: str) -> bool:
        """
        Check if photo is geotagged without downloading the full image.
        
        Args:
            photo_url: URL of the photo
            
        Returns:
            True if photo is geotagged, False otherwise
        """
        try:
            # Download just the EXIF data
            response = requests.get(photo_url, timeout=10)
            response.raise_for_status()
            
            # Load image and check for GPS data
            image = Image.open(io.BytesIO(response.content))
            exif = image._getexif()
            
            if exif is None:
                return False
            
            # Check for GPS info
            gps_info = exif.get(ExifTags.TAGS.get('GPSInfo', 'GPSInfo'))
            return gps_info is not None
            
        except Exception as e:
            logger.warning(f"Failed to check if photo is geotagged: {str(e)}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Test the photo processor
    processor = PhotoProcessor()
    
    # Test with a geotagged photo URL
    test_photo_url = "https://example.com/geotagged_photo.jpg"
    
    try:
        # Check if photo is geotagged
        if processor.is_geotagged(test_photo_url):
            print("Photo is geotagged!")
            
            # Process the photo
            result = processor.process_geotagged_photo(test_photo_url)
            
            print("Photo processed successfully!")
            print(f"GPS Coordinates: ({result['gps_coordinates']['latitude']}, {result['gps_coordinates']['longitude']})")
            print(f"Quality Score: {result['quality_score']:.3f}")
            
        else:
            print("Photo is not geotagged!")
            
    except ValueError as e:
        print(f"Photo processing failed: {e}")
