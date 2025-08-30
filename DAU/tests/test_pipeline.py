"""
Unit tests for the Community Mangrove Watch pipeline.
"""
import unittest
import json
import numpy as np
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from src.preprocessing.report_processor import ReportProcessor
from src.satellite.data_fetcher import SatelliteDataFetcher
from src.models.mangrove_validator import MangroveValidator, SwinUMambaSegmentation
from src.utils.result_processor import ResultProcessor
from src.pipeline.mangrove_pipeline import MangrovePipeline


class TestReportProcessor(unittest.TestCase):
    """Test cases for report preprocessing."""
    
    def setUp(self):
        self.processor = ReportProcessor()
        
        self.valid_report = {
            "photo_url": "https://example.com/photo.jpg",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "timestamp": "2024-01-15T10:30:00Z",
            "description": "Suspected illegal mangrove cutting",
            "reporter_id": "user123"
        }
    
    def test_parse_valid_report(self):
        """Test parsing a valid report."""
        with patch('src.preprocessing.report_processor.requests.get') as mock_get:
            # Mock successful photo download
            mock_response = Mock()
            mock_response.content = b'fake_image_data'
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            with patch('PIL.Image.open') as mock_image:
                # Mock image processing
                mock_img = Mock()
                mock_img.size = (1024, 768)
                mock_img.mode = 'RGB'
                mock_img.convert.return_value = mock_img
                mock_image.return_value = mock_img
                
                result = self.processor.parse_report_json(self.valid_report)
                
                self.assertIn('report_id', result)
                self.assertEqual(result['reporter_id'], 'user123')
                self.assertEqual(result['latitude'], 12.3456)
                self.assertEqual(result['longitude'], 78.9012)
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        invalid_report = self.valid_report.copy()
        invalid_report['latitude'] = 100.0  # Invalid latitude
        
        with self.assertRaises(ValueError):
            self.processor.parse_report_json(invalid_report)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_report = {
            "latitude": 12.3456,
            "longitude": 78.9012
            # Missing timestamp and reporter_id
        }
        
        with self.assertRaises(ValueError):
            self.processor.parse_report_json(incomplete_report)
    
    def test_invalid_timestamp(self):
        """Test handling of invalid timestamp."""
        invalid_report = self.valid_report.copy()
        invalid_report['timestamp'] = "invalid_timestamp"
        
        with self.assertRaises(ValueError):
            self.processor.parse_report_json(invalid_report)


class TestSatelliteDataFetcher(unittest.TestCase):
    """Test cases for satellite data fetching."""
    
    def setUp(self):
        self.fetcher = SatelliteDataFetcher(data_source="sentinel_hub")
    
    @patch('src.satellite.data_fetcher.SHConfig')
    def test_sentinel_hub_setup(self, mock_config):
        """Test Sentinel Hub configuration setup."""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        fetcher = SatelliteDataFetcher(data_source="sentinel_hub")
        
        self.assertEqual(fetcher.data_source, "sentinel_hub")
        self.assertIsNotNone(fetcher.config)
    
    def test_invalid_data_source(self):
        """Test handling of invalid data source."""
        with self.assertRaises(ValueError):
            SatelliteDataFetcher(data_source="invalid_source")
    
    @patch('src.satellite.data_fetcher.BBox')
    @patch('src.satellite.data_fetcher.SentinelHubRequest')
    def test_fetch_sentinel2_image(self, mock_request, mock_bbox):
        """Test fetching Sentinel-2 image."""
        # Mock the request and response
        mock_request_instance = Mock()
        mock_request_instance.get_data.return_value = [{
            'B02': np.random.random((512, 512)),
            'B03': np.random.random((512, 512)),
            'B04': np.random.random((512, 512)),
            'B08': np.random.random((512, 512))
        }]
        mock_request.return_value = mock_request_instance
        
        result = self.fetcher.fetch_sentinel2_image(
            latitude=12.3456,
            longitude=78.9012,
            image_size=256
        )
        
        self.assertIn('image_array', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['source'], 'sentinel_hub')


class TestMangroveValidator(unittest.TestCase):
    """Test cases for mangrove validation."""
    
    def setUp(self):
        self.validator = MangroveValidator()
    
    def test_model_initialization(self):
        """Test model initialization."""
        self.assertIsNotNone(self.validator.segmentation_model)
        self.assertIsNotNone(self.validator.anomaly_detector)
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        # Create dummy image
        image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        tensor = self.validator._preprocess_image(image)
        
        self.assertEqual(tensor.shape[0], 1)  # Batch dimension
        self.assertEqual(tensor.shape[1], 3)  # Channels
        self.assertEqual(tensor.shape[2], 512)  # Height
        self.assertEqual(tensor.shape[3], 512)  # Width
    
    def test_calculate_segmentation_confidence(self):
        """Test segmentation confidence calculation."""
        # Create dummy segmentation mask
        segmentation = np.random.random((1, 512, 512))
        segmentation_tensor = self.validator._preprocess_image(
            (segmentation * 255).astype(np.uint8)
        )
        
        confidence = self.validator._calculate_segmentation_confidence(segmentation_tensor)
        
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        # Create dummy segmentations
        citizen_seg = np.random.random((1, 512, 512))
        satellite_seg = np.random.random((1, 512, 512))
        location = (12.3456, 78.9012)
        
        citizen_tensor = self.validator._preprocess_image(
            (citizen_seg * 255).astype(np.uint8)
        )
        satellite_tensor = self.validator._preprocess_image(
            (satellite_seg * 255).astype(np.uint8)
        )
        
        anomaly_score, anomaly_detected = self.validator._detect_anomalies(
            citizen_tensor, satellite_tensor, location
        )
        
        self.assertGreaterEqual(anomaly_score, 0.0)
        self.assertLessEqual(anomaly_score, 1.0)
        self.assertIsInstance(anomaly_detected, bool)


class TestResultProcessor(unittest.TestCase):
    """Test cases for result processing."""
    
    def setUp(self):
        self.processor = ResultProcessor()
        
        self.validation_result = {
            'confidence_score': 0.85,
            'anomaly_detected': True,
            'anomaly_score': 0.75,
            'citizen_confidence': 0.82,
            'satellite_confidence': 0.88,
            'inference_time': 1.23,
            'citizen_segmentation': np.random.random((1, 512, 512)),
            'satellite_segmentation': np.random.random((1, 512, 512)),
            'metadata': {
                'model_used': 'Swin-UMamba',
                'location': (12.3456, 78.9012)
            }
        }
        
        self.report_data = {
            'report_id': 'test_report_123',
            'reporter_id': 'user456',
            'description': 'Suspected illegal mangrove cutting'
        }
    
    def test_determine_confidence_level(self):
        """Test confidence level determination."""
        self.assertEqual(self.processor._determine_confidence_level(0.9), 'high')
        self.assertEqual(self.processor._determine_confidence_level(0.7), 'medium')
        self.assertEqual(self.processor._determine_confidence_level(0.3), 'low')
        self.assertEqual(self.processor._determine_confidence_level(0.1), 'very_low')
    
    def test_determine_urgency_level(self):
        """Test urgency level determination."""
        urgency = self.processor._determine_urgency_level(0.85, 0.75, True)
        self.assertIn(urgency, ['low', 'medium', 'high', 'critical'])
    
    def test_calculate_points(self):
        """Test points calculation."""
        points = self.processor._calculate_points(0.85, True, 'high')
        self.assertGreater(points, 0)
    
    def test_process_validation_result(self):
        """Test complete result processing."""
        result = self.processor.process_validation_result(
            self.validation_result, self.report_data
        )
        
        self.assertIn('confidence_score', result)
        self.assertIn('anomaly_detected', result)
        self.assertIn('urgency_level', result)
        self.assertIn('summary', result)
        self.assertIn('points_earned', result)
        self.assertIn('badges', result)


class TestMangrovePipeline(unittest.TestCase):
    """Test cases for the complete pipeline."""
    
    def setUp(self):
        self.pipeline = MangrovePipeline()
        
        self.valid_report = {
            "photo_url": "https://example.com/photo.jpg",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "timestamp": "2024-01-15T10:30:00Z",
            "description": "Suspected illegal mangrove cutting",
            "reporter_id": "user123"
        }
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        self.assertIsNotNone(self.pipeline.report_processor)
        self.assertIsNotNone(self.pipeline.satellite_fetcher)
        self.assertIsNotNone(self.pipeline.mangrove_validator)
        self.assertIsNotNone(self.pipeline.result_processor)
    
    def test_validate_input(self):
        """Test input validation."""
        validation = self.pipeline.validate_input(self.valid_report)
        self.assertTrue(validation['valid'])
        
        # Test invalid input
        invalid_report = self.valid_report.copy()
        invalid_report['latitude'] = 100.0
        validation = self.pipeline.validate_input(invalid_report)
        self.assertFalse(validation['valid'])
    
    def test_get_pipeline_status(self):
        """Test pipeline status retrieval."""
        status = self.pipeline.get_pipeline_status()
        self.assertIn('status', status)
        self.assertIn('components', status)
        self.assertIn('configuration', status)
    
    @patch('src.preprocessing.report_processor.requests.get')
    @patch('src.satellite.data_fetcher.SentinelHubRequest')
    def test_complete_pipeline(self, mock_request, mock_get):
        """Test complete pipeline processing."""
        # Mock all external dependencies
        mock_get.return_value.content = b'fake_image_data'
        mock_get.return_value.raise_for_status.return_value = None
        
        mock_request_instance = Mock()
        mock_request_instance.get_data.return_value = [{
            'B02': np.random.random((512, 512)),
            'B03': np.random.random((512, 512)),
            'B04': np.random.random((512, 512)),
            'B08': np.random.random((512, 512))
        }]
        mock_request.return_value = mock_request_instance
        
        # Mock image processing
        with patch('PIL.Image.open'):
            result = self.pipeline.process_report(self.valid_report)
            
            self.assertIn('report_id', result)
            self.assertIn('confidence_score', result)
            self.assertIn('anomaly_detected', result)
            self.assertIn('urgency_level', result)
            self.assertIn('processing_metadata', result)


class TestSwinUMambaSegmentation(unittest.TestCase):
    """Test cases for the Swin-UMamba segmentation model."""
    
    def setUp(self):
        self.model = SwinUMambaSegmentation(num_classes=1, input_channels=3)
    
    def test_model_architecture(self):
        """Test model architecture."""
        self.assertIsNotNone(self.model.encoder)
        self.assertIsNotNone(self.model.decoder)
    
    def test_forward_pass(self):
        """Test model forward pass."""
        # Create dummy input
        x = np.random.random((1, 3, 512, 512)).astype(np.float32)
        x_tensor = torch.from_numpy(x)
        
        with torch.no_grad():
            output = self.model(x_tensor)
            
            self.assertEqual(output.shape[0], 1)  # Batch size
            self.assertEqual(output.shape[1], 1)  # Number of classes
            self.assertEqual(output.shape[2], 512)  # Height
            self.assertEqual(output.shape[3], 512)  # Width
    
    def test_model_parameters(self):
        """Test model parameters."""
        total_params = sum(p.numel() for p in self.model.parameters())
        self.assertGreater(total_params, 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
