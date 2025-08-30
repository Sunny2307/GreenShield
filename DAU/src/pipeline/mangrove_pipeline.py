"""
Main pipeline orchestrator for Community Mangrove Watch.
Coordinates all components for end-to-end processing of citizen reports.
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from src.preprocessing.report_processor import ReportProcessor
from src.satellite.data_fetcher import SatelliteDataFetcher
from src.models.mangrove_validator import MangroveValidator
from src.utils.result_processor import ResultProcessor
from src.utils.logger import log_report_processing
from config.settings import settings


class MangrovePipeline:
    """
    Main pipeline for processing citizen mangrove reports.
    """
    
    def __init__(self):
        """Initialize the pipeline components."""
        self.report_processor = ReportProcessor()
        self.satellite_fetcher = SatelliteDataFetcher(
            data_source=settings.satellite.default_source
        )
        self.mangrove_validator = MangroveValidator()
        self.result_processor = ResultProcessor()
        
        logger.info("Mangrove pipeline initialized successfully")
    
    def process_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a citizen report through the complete pipeline.
        
        Args:
            report_data: Raw citizen report data
            
        Returns:
            Complete validation results with recommendations
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting pipeline processing for report")
            
            # Step 1: Preprocess and validate report
            logger.info("Step 1: Preprocessing report")
            structured_report = self.report_processor.parse_report_json(report_data)
            structured_report = self.report_processor.validate_report_quality(structured_report)
            
            # Step 2: Fetch satellite data
            logger.info("Step 2: Fetching satellite data")
            satellite_data = self.satellite_fetcher.fetch_sentinel2_image(
                latitude=structured_report['latitude'],
                longitude=structured_report['longitude'],
                image_size=settings.satellite.image_size,
                cloud_coverage_threshold=settings.satellite.cloud_coverage_threshold
            )
            
            # Step 3: AI validation (if photo is available)
            validation_result = None
            if structured_report['photo_data']:
                logger.info("Step 3: Running AI validation")
                validation_result = self.mangrove_validator.validate_report(
                    citizen_photo=structured_report['photo_data']['image_array'],
                    satellite_image=satellite_data['image_array'],
                    location=(structured_report['latitude'], structured_report['longitude'])
                )
            else:
                logger.warning("No photo data available, skipping AI validation")
                # Create default validation result for reports without photos
                validation_result = self._create_default_validation_result(
                    structured_report, satellite_data
                )
            
            # Step 4: Process results and generate response
            logger.info("Step 4: Processing results")
            final_response = self.result_processor.process_validation_result(
                validation_result, structured_report
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log processing results
            log_report_processing(
                report_id=structured_report['report_id'],
                reporter_id=structured_report['reporter_id'],
                latitude=structured_report['latitude'],
                longitude=structured_report['longitude'],
                processing_time=processing_time,
                confidence_score=final_response['confidence_score'],
                anomaly_detected=final_response['anomaly_detected']
            )
            
            # Add processing metadata
            final_response['processing_metadata'] = {
                'processing_time': round(processing_time, 3),
                'pipeline_version': '1.0.0',
                'components_used': [
                    'report_processor',
                    'satellite_fetcher',
                    'mangrove_validator',
                    'result_processor'
                ],
                'satellite_data_source': settings.satellite.default_source,
                'satellite_cloud_coverage': satellite_data['metadata']['cloud_coverage']
            }
            
            logger.info(f"Pipeline processing completed successfully in {processing_time:.2f}s")
            return final_response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Pipeline processing failed: {str(e)}"
            
            # Log error
            log_report_processing(
                report_id=report_data.get('report_id', 'unknown'),
                reporter_id=report_data.get('reporter_id', 'unknown'),
                latitude=report_data.get('latitude', 0.0),
                longitude=report_data.get('longitude', 0.0),
                processing_time=processing_time,
                confidence_score=0.0,
                anomaly_detected=False,
                error=error_msg
            )
            
            logger.error(error_msg)
            raise
    
    def _create_default_validation_result(
        self,
        structured_report: Dict[str, Any],
        satellite_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create default validation result for reports without photos.
        
        Args:
            structured_report: Structured report data
            satellite_data: Satellite image data
            
        Returns:
            Default validation result
        """
        # Run segmentation only on satellite image
        validation_result = self.mangrove_validator.validate_report(
            citizen_photo=satellite_data['image_array'],  # Use satellite as citizen photo
            satellite_image=satellite_data['image_array'],
            location=(structured_report['latitude'], structured_report['longitude'])
        )
        
        # Adjust confidence scores for reports without photos
        validation_result['confidence_score'] *= 0.5  # Reduce confidence
        validation_result['citizen_confidence'] *= 0.3  # Much lower citizen confidence
        
        return validation_result
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and health metrics.
        
        Returns:
            Pipeline status information
        """
        try:
            status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'report_processor': 'ready',
                    'satellite_fetcher': 'ready',
                    'mangrove_validator': 'ready',
                    'result_processor': 'ready'
                },
                'configuration': {
                    'satellite_source': settings.satellite.default_source,
                    'model_confidence_threshold': settings.model.confidence_threshold,
                    'anomaly_threshold': settings.model.anomaly_threshold,
                    'image_size': settings.satellite.image_size
                },
                'model_info': {
                    'segmentation_model': 'Swin-UMamba',
                    'anomaly_detector': 'IsolationForest',
                    'device': str(self.mangrove_validator.device)
                }
            }
            
            # Check component health
            try:
                # Test satellite fetcher
                self.satellite_fetcher.fetch_sentinel2_image(
                    latitude=0.0, longitude=0.0, image_size=64
                )
            except Exception as e:
                status['components']['satellite_fetcher'] = f'error: {str(e)}'
                status['status'] = 'degraded'
            
            return status
            
        except Exception as e:
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def validate_input(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input report data before processing.
        
        Args:
            report_data: Raw report data
            
        Returns:
            Validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields (latitude and longitude are now extracted from photos)
        required_fields = ['photo_url', 'timestamp', 'reporter_id']
        for field in required_fields:
            if field not in report_data:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Missing required field: {field}")
        
        # Validate photo URL format
        if 'photo_url' in report_data:
            photo_url = report_data['photo_url']
            if not isinstance(photo_url, str) or not photo_url.startswith(('http://', 'https://')):
                validation_result['valid'] = False
                validation_result['errors'].append("Invalid photo URL format")
        
        # Note: Latitude and longitude are now extracted from geotagged photos
        # No need to validate them here as they're extracted during processing
        
        # Photo URL is now required, so no warning needed
        
        # Check description length
        if 'description' in report_data:
            desc_length = len(report_data['description'])
            if desc_length < 10:
                validation_result['warnings'].append("Description is very short")
            elif desc_length > 1000:
                validation_result['warnings'].append("Description is very long")
        
        return validation_result
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics and metrics.
        
        Returns:
            Processing statistics
        """
        # This would typically be implemented with a database or metrics store
        # For now, return basic structure
        return {
            'total_reports_processed': 0,
            'average_processing_time': 0.0,
            'success_rate': 1.0,
            'anomaly_detection_rate': 0.0,
            'average_confidence_score': 0.0,
            'most_common_urgency_level': 'low',
            'top_reporting_locations': [],
            'recent_activity': {
                'last_24_hours': 0,
                'last_7_days': 0,
                'last_30_days': 0
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the complete pipeline
    try:
        pipeline = MangrovePipeline()
        
        # Sample report data
        sample_report = {
            "photo_url": "https://example.com/mangrove_photo.jpg",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "timestamp": "2024-01-15T10:30:00Z",
            "description": "Suspected illegal mangrove cutting in the area",
            "reporter_id": "user123"
        }
        
        # Validate input
        validation = pipeline.validate_input(sample_report)
        print(f"Input validation: {validation}")
        
        if validation['valid']:
            # Process report
            result = pipeline.process_report(sample_report)
            
            print("Pipeline processing completed!")
            print(f"Report ID: {result['report_id']}")
            print(f"Confidence Score: {result['confidence_score']}")
            print(f"Anomaly Detected: {result['anomaly_detected']}")
            print(f"Urgency Level: {result['urgency_level']}")
            print(f"Points Earned: {result['points_earned']}")
            print(f"Processing Time: {result['processing_metadata']['processing_time']}s")
        else:
            print("Input validation failed!")
            for error in validation['errors']:
                print(f"Error: {error}")
        
        # Get pipeline status
        status = pipeline.get_pipeline_status()
        print(f"Pipeline Status: {status['status']}")
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        print("Note: This requires valid API credentials and model files to work properly.")
