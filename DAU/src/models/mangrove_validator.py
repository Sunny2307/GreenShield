"""
AI validation module for Community Mangrove Watch.
Handles mangrove segmentation and anomaly detection using state-of-the-art models.
"""
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import cv2
from loguru import logger
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from config.settings import settings
from src.utils.logger import log_model_inference


class SwinUMambaSegmentation(nn.Module):
    """
    Swin-UMamba model for mangrove segmentation.
    Adapted from the MangroveAI implementation.
    """
    
    def __init__(self, num_classes: int = 1, input_channels: int = 3):
        super(SwinUMambaSegmentation, self).__init__()
        
        # Simplified Swin-UMamba architecture
        # In practice, you would use the full implementation from MangroveAI
        
        # Encoder (Swin Transformer)
        self.encoder = self._build_encoder(input_channels)
        
        # Decoder (Mamba-based)
        self.decoder = self._build_decoder(num_classes)
        
        # Initialize weights
        self._initialize_weights()
    
    def _build_encoder(self, input_channels: int) -> nn.Module:
        """Build the Swin Transformer encoder."""
        # Simplified encoder - in practice, use the full Swin Transformer
        return nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            # Additional encoder layers would go here
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
        )
    
    def _build_decoder(self, num_classes: int) -> nn.Module:
        """Build the Mamba-based decoder."""
        # Simplified decoder - in practice, use the full Mamba implementation
        return nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(32, num_classes, kernel_size=4, stride=2, padding=1),
            nn.Sigmoid()
        )
    
    def _initialize_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """Forward pass."""
        # Encoder
        features = self.encoder(x)
        
        # Decoder
        output = self.decoder(features)
        
        return output


class MangroveValidator:
    """
    Validates mangrove reports using AI models for segmentation and anomaly detection.
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.segmentation_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        
        # Load models
        self._load_segmentation_model()
        self._load_anomaly_detector()
    
    def _load_segmentation_model(self):
        """Load the pre-trained mangrove segmentation model."""
        try:
            # Initialize model
            self.segmentation_model = SwinUMambaSegmentation(
                num_classes=1,
                input_channels=3
            )
            
            # Load pre-trained weights if available
            model_path = settings.model.mangrove_segmentation_model_path
            if os.path.exists(model_path):
                self.segmentation_model.load_state_dict(
                    torch.load(model_path, map_location=self.device)
                )
                logger.info(f"Loaded segmentation model from {model_path}")
            else:
                logger.warning(f"Model weights not found at {model_path}. Using random initialization.")
            
            self.segmentation_model.to(self.device)
            self.segmentation_model.eval()
            
        except Exception as e:
            logger.error(f"Failed to load segmentation model: {str(e)}")
            raise
    
    def _load_anomaly_detector(self):
        """Load the anomaly detection model."""
        try:
            model_path = settings.model.anomaly_detection_model_path
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)
                logger.info(f"Loaded anomaly detector from {model_path}")
            else:
                # Initialize new anomaly detector
                self.anomaly_detector = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                logger.info("Initialized new anomaly detector")
            
        except Exception as e:
            logger.error(f"Failed to load anomaly detector: {str(e)}")
            raise
    
    def validate_report(
        self,
        citizen_photo: np.ndarray,
        satellite_image: np.ndarray,
        location: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Validate a citizen report by comparing photo with satellite data.
        
        Args:
            citizen_photo: Citizen's geotagged photo
            satellite_image: Corresponding satellite image
            location: (latitude, longitude) coordinates
            
        Returns:
            Validation results with confidence scores and anomaly flags
        """
        try:
            start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
            end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
            
            if start_time:
                start_time.record()
            
            # Preprocess images
            citizen_tensor = self._preprocess_image(citizen_photo)
            satellite_tensor = self._preprocess_image(satellite_image)
            
            # Run segmentation on both images
            citizen_segmentation = self._segment_mangroves(citizen_tensor)
            satellite_segmentation = self._segment_mangroves(satellite_tensor)
            
            if end_time:
                end_time.record()
                torch.cuda.synchronize()
                inference_time = start_time.elapsed_time(end_time) / 1000.0
            else:
                inference_time = 0.0
            
            # Calculate confidence scores
            citizen_confidence = self._calculate_segmentation_confidence(citizen_segmentation)
            satellite_confidence = self._calculate_segmentation_confidence(satellite_segmentation)
            
            # Detect anomalies
            anomaly_score, anomaly_detected = self._detect_anomalies(
                citizen_segmentation, satellite_segmentation, location
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                citizen_confidence, satellite_confidence, anomaly_score
            )
            
            # Generate validation result
            validation_result = {
                'confidence_score': overall_confidence,
                'anomaly_detected': anomaly_detected,
                'anomaly_score': anomaly_score,
                'citizen_confidence': citizen_confidence,
                'satellite_confidence': satellite_confidence,
                'citizen_segmentation': citizen_segmentation.cpu().numpy(),
                'satellite_segmentation': satellite_segmentation.cpu().numpy(),
                'inference_time': inference_time,
                'metadata': {
                    'model_used': 'Swin-UMamba',
                    'location': location,
                    'segmentation_threshold': settings.model.segmentation_threshold
                }
            }
            
            log_model_inference(
                'Swin-UMamba',
                citizen_photo.shape,
                inference_time,
                overall_confidence
            )
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            log_model_inference('Swin-UMamba', citizen_photo.shape, 0.0, 0.0, error_msg)
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image array
            
        Returns:
            Preprocessed tensor
        """
        # Ensure image is in the correct format
        if len(image.shape) == 3 and image.shape[2] == 3:
            # RGB image
            image = image.astype(np.float32) / 255.0
        else:
            raise ValueError(f"Expected RGB image, got shape {image.shape}")
        
        # Resize to model input size
        target_size = settings.model.input_size
        if image.shape[:2] != (target_size, target_size):
            image = cv2.resize(image, (target_size, target_size))
        
        # Convert to tensor and add batch dimension
        image_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)
        
        # Normalize
        mean = torch.tensor(settings.model.normalize_mean).view(3, 1, 1)
        std = torch.tensor(settings.model.normalize_std).view(3, 1, 1)
        image_tensor = (image_tensor - mean) / std
        
        return image_tensor.to(self.device)
    
    def _segment_mangroves(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """
        Segment mangroves in the image.
        
        Args:
            image_tensor: Preprocessed image tensor
            
        Returns:
            Segmentation mask
        """
        with torch.no_grad():
            # Forward pass
            output = self.segmentation_model(image_tensor)
            
            # Apply threshold
            mask = (output > settings.model.segmentation_threshold).float()
            
            return mask
    
    def _calculate_segmentation_confidence(self, segmentation: torch.Tensor) -> float:
        """
        Calculate confidence score for segmentation.
        
        Args:
            segmentation: Segmentation mask
            
        Returns:
            Confidence score between 0 and 1
        """
        # Calculate confidence based on segmentation quality
        # Higher confidence for clear, well-defined mangrove areas
        
        # Convert to numpy for processing
        mask = segmentation.cpu().numpy().squeeze()
        
        # Calculate various metrics
        mangrove_coverage = np.mean(mask)
        
        # Edge density (well-defined boundaries)
        edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
        edge_density = np.mean(edges > 0)
        
        # Spatial coherence (connected components)
        num_components, _ = cv2.connectedComponents((mask * 255).astype(np.uint8))
        coherence_score = 1.0 / (1.0 + num_components)  # Fewer components = more coherent
        
        # Combine metrics
        confidence = (
            mangrove_coverage * 0.4 +
            edge_density * 0.3 +
            coherence_score * 0.3
        )
        
        return min(1.0, max(0.0, confidence))
    
    def _detect_anomalies(
        self,
        citizen_segmentation: torch.Tensor,
        satellite_segmentation: torch.Tensor,
        location: Tuple[float, float]
    ) -> Tuple[float, bool]:
        """
        Detect anomalies by comparing citizen and satellite segmentations.
        
        Args:
            citizen_segmentation: Citizen photo segmentation
            satellite_segmentation: Satellite image segmentation
            location: Location coordinates
            
        Returns:
            (anomaly_score, anomaly_detected)
        """
        try:
            # Convert to numpy
            citizen_mask = citizen_segmentation.cpu().numpy().squeeze()
            satellite_mask = satellite_segmentation.cpu().numpy().squeeze()
            
            # Calculate difference metrics
            difference = np.abs(citizen_mask - satellite_mask)
            mean_difference = np.mean(difference)
            
            # Calculate IoU (Intersection over Union)
            intersection = np.logical_and(citizen_mask > 0.5, satellite_mask > 0.5)
            union = np.logical_or(citizen_mask > 0.5, satellite_mask > 0.5)
            
            if np.sum(union) > 0:
                iou = np.sum(intersection) / np.sum(union)
            else:
                iou = 0.0
            
            # Calculate mangrove coverage difference
            citizen_coverage = np.mean(citizen_mask)
            satellite_coverage = np.mean(satellite_mask)
            coverage_difference = abs(citizen_coverage - satellite_coverage)
            
            # Create feature vector for anomaly detection
            features = np.array([
                mean_difference,
                1.0 - iou,  # IoU difference
                coverage_difference,
                citizen_coverage,
                satellite_coverage,
                location[0],  # latitude
                location[1]   # longitude
            ]).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Predict anomaly
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            anomaly_detected = anomaly_score < settings.model.anomaly_threshold
            
            # Normalize anomaly score to 0-1 range
            normalized_score = max(0.0, min(1.0, (anomaly_score + 0.5)))
            
            return normalized_score, anomaly_detected
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return 0.5, False  # Default values
    
    def _calculate_overall_confidence(
        self,
        citizen_confidence: float,
        satellite_confidence: float,
        anomaly_score: float
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            citizen_confidence: Confidence in citizen photo segmentation
            satellite_confidence: Confidence in satellite image segmentation
            anomaly_score: Anomaly detection score
            
        Returns:
            Overall confidence score
        """
        # Weight the different confidence scores
        weights = {
            'citizen': 0.4,
            'satellite': 0.4,
            'anomaly': 0.2
        }
        
        # Anomaly score is inverted (lower is better)
        anomaly_confidence = 1.0 - anomaly_score
        
        overall_confidence = (
            citizen_confidence * weights['citizen'] +
            satellite_confidence * weights['satellite'] +
            anomaly_confidence * weights['anomaly']
        )
        
        return min(1.0, max(0.0, overall_confidence))
    
    def save_models(self):
        """Save the trained models."""
        try:
            # Save segmentation model
            os.makedirs(os.path.dirname(settings.model.mangrove_segmentation_model_path), exist_ok=True)
            torch.save(
                self.segmentation_model.state_dict(),
                settings.model.mangrove_segmentation_model_path
            )
            
            # Save anomaly detector
            os.makedirs(os.path.dirname(settings.model.anomaly_detection_model_path), exist_ok=True)
            with open(settings.model.anomaly_detection_model_path, 'wb') as f:
                pickle.dump(self.anomaly_detector, f)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {str(e)}")
            raise


# Example usage and testing
if __name__ == "__main__":
    # Test the mangrove validator
    try:
        validator = MangroveValidator()
        
        # Create dummy images for testing
        citizen_photo = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        satellite_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        location = (12.3456, 78.9012)
        
        # Validate report
        result = validator.validate_report(citizen_photo, satellite_image, location)
        
        print("Validation completed successfully!")
        print(f"Confidence Score: {result['confidence_score']:.3f}")
        print(f"Anomaly Detected: {result['anomaly_detected']}")
        print(f"Anomaly Score: {result['anomaly_score']:.3f}")
        print(f"Inference Time: {result['inference_time']:.3f}s")
        
    except Exception as e:
        print(f"Validation failed: {e}")
