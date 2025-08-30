"""
Result postprocessing module for Community Mangrove Watch.
Handles generation of structured responses and gamification features.
"""
import json
import base64
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from loguru import logger

from config.settings import settings


class ResultProcessor:
    """
    Processes AI validation results and generates structured responses.
    """
    
    def __init__(self):
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        self.urgency_thresholds = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3
        }
    
    def process_validation_result(
        self,
        validation_result: Dict[str, Any],
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process AI validation results and generate structured response.
        
        Args:
            validation_result: Results from AI validation
            report_data: Original report data
            
        Returns:
            Structured response with confidence, urgency, and summary
        """
        try:
            # Extract key metrics
            confidence_score = validation_result['confidence_score']
            anomaly_detected = validation_result['anomaly_detected']
            anomaly_score = validation_result['anomaly_score']
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(confidence_score)
            
            # Determine urgency level
            urgency_level = self._determine_urgency_level(
                confidence_score, anomaly_score, anomaly_detected
            )
            
            # Generate human-readable summary
            summary = self._generate_summary(
                confidence_score, anomaly_detected, anomaly_score,
                report_data, validation_result
            )
            
            # Calculate gamification points
            points = self._calculate_points(
                confidence_score, anomaly_detected, urgency_level
            )
            
            # Encode segmentation masks
            citizen_mask_b64 = self._encode_mask(validation_result['citizen_segmentation'])
            satellite_mask_b64 = self._encode_mask(validation_result['satellite_segmentation'])
            
            # Create structured response
            response = {
                'report_id': report_data['report_id'],
                'reporter_id': report_data['reporter_id'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                
                # Validation results
                'confidence_score': round(confidence_score, 3),
                'confidence_level': confidence_level,
                'anomaly_detected': anomaly_detected,
                'anomaly_score': round(anomaly_score, 3),
                'urgency_level': urgency_level,
                
                # Detailed metrics
                'citizen_confidence': round(validation_result['citizen_confidence'], 3),
                'satellite_confidence': round(validation_result['satellite_confidence'], 3),
                'inference_time': round(validation_result['inference_time'], 3),
                
                # Visualizations
                'citizen_segmentation_mask': citizen_mask_b64,
                'satellite_segmentation_mask': satellite_mask_b64,
                
                # Summary and recommendations
                'summary': summary,
                'recommendations': self._generate_recommendations(
                    confidence_level, anomaly_detected, urgency_level
                ),
                
                # Gamification
                'points_earned': points,
                'badges': self._determine_badges(confidence_score, anomaly_detected),
                
                # Metadata
                'metadata': {
                    'model_used': validation_result['metadata']['model_used'],
                    'location': validation_result['metadata']['location'],
                    'processing_version': '1.0.0'
                }
            }
            
            logger.info(f"Result processed for report {report_data['report_id']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process validation result: {str(e)}")
            raise
    
    def _determine_confidence_level(self, confidence_score: float) -> str:
        """
        Determine confidence level based on score.
        
        Args:
            confidence_score: AI confidence score
            
        Returns:
            Confidence level string
        """
        if confidence_score >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence_score >= self.confidence_thresholds['medium']:
            return 'medium'
        elif confidence_score >= self.confidence_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def _determine_urgency_level(
        self,
        confidence_score: float,
        anomaly_score: float,
        anomaly_detected: bool
    ) -> str:
        """
        Determine urgency level based on validation results.
        
        Args:
            confidence_score: AI confidence score
            anomaly_score: Anomaly detection score
            anomaly_detected: Whether anomaly was detected
            
        Returns:
            Urgency level string
        """
        # Calculate urgency score
        urgency_score = 0.0
        
        # High confidence anomalies are more urgent
        if anomaly_detected and confidence_score > 0.7:
            urgency_score += 0.4
        
        # High anomaly scores increase urgency
        urgency_score += anomaly_score * 0.3
        
        # High confidence in general increases urgency
        urgency_score += confidence_score * 0.3
        
        # Determine urgency level
        if urgency_score >= self.urgency_thresholds['critical']:
            return 'critical'
        elif urgency_score >= self.urgency_thresholds['high']:
            return 'high'
        elif urgency_score >= self.urgency_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _generate_summary(
        self,
        confidence_score: float,
        anomaly_detected: bool,
        anomaly_score: float,
        report_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable summary of validation results.
        
        Args:
            confidence_score: AI confidence score
            anomaly_detected: Whether anomaly was detected
            anomaly_score: Anomaly detection score
            report_data: Original report data
            validation_result: Validation results
            
        Returns:
            Human-readable summary
        """
        confidence_level = self._determine_confidence_level(confidence_score)
        
        if anomaly_detected:
            if confidence_level == 'high':
                summary = (
                    f"High confidence anomaly detected at the reported location. "
                    f"The AI analysis shows significant differences between the citizen photo "
                    f"and satellite imagery, suggesting potential illegal activity or "
                    f"environmental changes. Anomaly score: {anomaly_score:.1%}. "
                    f"Immediate investigation recommended."
                )
            elif confidence_level == 'medium':
                summary = (
                    f"Medium confidence anomaly detected. The analysis indicates "
                    f"potential discrepancies between the citizen report and satellite data. "
                    f"Anomaly score: {anomaly_score:.1%}. "
                    f"Further investigation advised."
                )
            else:
                summary = (
                    f"Low confidence anomaly detected. While some differences were found "
                    f"between the citizen photo and satellite imagery, the AI confidence "
                    f"is limited. Anomaly score: {anomaly_score:.1%}. "
                    f"Manual review recommended."
                )
        else:
            if confidence_level == 'high':
                summary = (
                    f"High confidence validation completed. The citizen report appears "
                    f"consistent with satellite imagery. No significant anomalies detected. "
                    f"Confidence score: {confidence_score:.1%}. "
                    f"Report appears reliable."
                )
            elif confidence_level == 'medium':
                summary = (
                    f"Medium confidence validation completed. The analysis shows "
                    f"general consistency between the citizen report and satellite data. "
                    f"Confidence score: {confidence_score:.1%}. "
                    f"Report appears mostly reliable."
                )
            else:
                summary = (
                    f"Low confidence validation completed. The AI analysis could not "
                    f"determine with high certainty whether the report is consistent "
                    f"with satellite data. Confidence score: {confidence_score:.1%}. "
                    f"Manual review recommended."
                )
        
        return summary
    
    def _generate_recommendations(
        self,
        confidence_level: str,
        anomaly_detected: bool,
        urgency_level: str
    ) -> list:
        """
        Generate recommendations based on validation results.
        
        Args:
            confidence_level: Confidence level
            anomaly_detected: Whether anomaly was detected
            urgency_level: Urgency level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if anomaly_detected:
            if urgency_level == 'critical':
                recommendations.extend([
                    "Immediate field investigation required",
                    "Notify local authorities and conservation teams",
                    "Document the site with additional photos",
                    "Monitor the area for further changes"
                ])
            elif urgency_level == 'high':
                recommendations.extend([
                    "Schedule field investigation within 24 hours",
                    "Notify relevant authorities",
                    "Request additional citizen reports from the area",
                    "Compare with historical satellite data"
                ])
            else:
                recommendations.extend([
                    "Schedule field investigation within 48 hours",
                    "Request additional photos from the reporter",
                    "Monitor satellite imagery for changes",
                    "Consider seasonal variations in mangrove cover"
                ])
        else:
            if confidence_level == 'high':
                recommendations.extend([
                    "Report appears reliable - no immediate action required",
                    "Continue monitoring the area through citizen reports",
                    "Thank the reporter for their contribution",
                    "Consider this area for regular satellite monitoring"
                ])
            else:
                recommendations.extend([
                    "Request additional photos from the reporter",
                    "Consider seasonal variations in mangrove appearance",
                    "Schedule follow-up satellite imagery analysis",
                    "Encourage continued citizen monitoring"
                ])
        
        return recommendations
    
    def _calculate_points(
        self,
        confidence_score: float,
        anomaly_detected: bool,
        urgency_level: str
    ) -> int:
        """
        Calculate gamification points for the report.
        
        Args:
            confidence_score: AI confidence score
            anomaly_detected: Whether anomaly was detected
            urgency_level: Urgency level
            
        Returns:
            Points earned
        """
        points = settings.gamification.base_points_per_report
        
        # Bonus for high confidence
        if confidence_score >= settings.gamification.high_confidence_threshold:
            points += settings.gamification.bonus_points_high_confidence
        
        # Bonus for anomaly detection
        if anomaly_detected:
            points += settings.gamification.bonus_points_anomaly_detected
        
        # Bonus for urgency level
        urgency_bonus = settings.gamification.urgency_levels.get(urgency_level, 0)
        points += urgency_bonus
        
        return points
    
    def _determine_badges(self, confidence_score: float, anomaly_detected: bool) -> list:
        """
        Determine badges earned for the report.
        
        Args:
            confidence_score: AI confidence score
            anomaly_detected: Whether anomaly was detected
            
        Returns:
            List of badges earned
        """
        badges = []
        
        # Quality badges
        if confidence_score >= 0.9:
            badges.append("gold_quality")
        elif confidence_score >= 0.8:
            badges.append("silver_quality")
        elif confidence_score >= 0.7:
            badges.append("bronze_quality")
        
        # Detection badges
        if anomaly_detected:
            badges.append("anomaly_detector")
            if confidence_score >= 0.8:
                badges.append("expert_detector")
        
        # Contribution badges
        badges.append("citizen_scientist")
        
        return badges
    
    def _encode_mask(self, mask: np.ndarray) -> str:
        """
        Encode segmentation mask as base64 string.
        
        Args:
            mask: Segmentation mask array
            
        Returns:
            Base64 encoded string
        """
        try:
            # Ensure mask is in the correct format
            if len(mask.shape) == 3:
                mask = mask.squeeze()
            
            # Convert to uint8 and scale to 0-255
            mask_uint8 = (mask * 255).astype(np.uint8)
            
            # Encode as base64
            mask_bytes = mask_uint8.tobytes()
            mask_b64 = base64.b64encode(mask_bytes).decode('utf-8')
            
            return mask_b64
            
        except Exception as e:
            logger.error(f"Failed to encode mask: {str(e)}")
            return ""
    
    def create_dashboard_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create data structure for dashboard visualization.
        
        Args:
            response: Processed validation response
            
        Returns:
            Dashboard-ready data structure
        """
        dashboard_data = {
            'report_summary': {
                'id': response['report_id'],
                'reporter': response['reporter_id'],
                'timestamp': response['timestamp'],
                'confidence': response['confidence_score'],
                'anomaly': response['anomaly_detected'],
                'urgency': response['urgency_level'],
                'points': response['points_earned']
            },
            'visualization_data': {
                'confidence_level': response['confidence_level'],
                'urgency_level': response['urgency_level'],
                'anomaly_score': response['anomaly_score'],
                'citizen_confidence': response['citizen_confidence'],
                'satellite_confidence': response['satellite_confidence']
            },
            'gamification': {
                'points_earned': response['points_earned'],
                'badges': response['badges'],
                'level_progress': self._calculate_level_progress(response['points_earned'])
            },
            'recommendations': response['recommendations'],
            'metadata': response['metadata']
        }
        
        return dashboard_data
    
    def _calculate_level_progress(self, points: int) -> Dict[str, Any]:
        """
        Calculate level progress for gamification.
        
        Args:
            points: Points earned
            
        Returns:
            Level progress data
        """
        # Define level thresholds
        level_thresholds = {
            'beginner': 0,
            'explorer': 50,
            'detector': 150,
            'expert': 300,
            'master': 500
        }
        
        current_level = 'beginner'
        next_level = 'explorer'
        progress = 0.0
        
        # Find current level
        for level, threshold in level_thresholds.items():
            if points >= threshold:
                current_level = level
        
        # Find next level and calculate progress
        levels = list(level_thresholds.keys())
        current_index = levels.index(current_level)
        
        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            current_threshold = level_thresholds[current_level]
            next_threshold = level_thresholds[next_level]
            progress = (points - current_threshold) / (next_threshold - current_threshold)
        else:
            progress = 1.0
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'progress': min(1.0, max(0.0, progress)),
            'points_to_next': max(0, level_thresholds.get(next_level, 0) - points)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the result processor
    processor = ResultProcessor()
    
    # Sample validation result
    validation_result = {
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
    
    # Sample report data
    report_data = {
        'report_id': 'test_report_123',
        'reporter_id': 'user456',
        'description': 'Suspected illegal mangrove cutting'
    }
    
    # Process results
    response = processor.process_validation_result(validation_result, report_data)
    
    print("Result processing completed!")
    print(f"Confidence Level: {response['confidence_level']}")
    print(f"Urgency Level: {response['urgency_level']}")
    print(f"Points Earned: {response['points_earned']}")
    print(f"Badges: {response['badges']}")
    print(f"Summary: {response['summary'][:100]}...")
