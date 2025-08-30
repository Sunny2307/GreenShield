"""
Integration example for Community Mangrove Watch pipeline.
Demonstrates how to use the complete system for processing citizen reports.
"""
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any

# Example API client for the mangrove monitoring system
class MangroveWatchClient:
    """Client for interacting with the Community Mangrove Watch API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def validate_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a citizen report for validation.
        
        Args:
            report_data: Citizen report data
            
        Returns:
            Validation results
        """
        url = f"{self.base_url}/validate-report"
        
        try:
            response = self.session.post(url, json=report_data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status."""
        url = f"{self.base_url}/status"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        url = f"{self.base_url}/statistics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connectivity."""
        url = f"{self.base_url}/test-connection"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()


def example_citizen_report():
    """Example of a citizen report submission."""
    
    # Initialize client
    client = MangroveWatchClient("http://localhost:8000")
    
    # Test connection first
    print("Testing API connection...")
    try:
        connection_test = client.test_connection()
        print(f"✓ Connection test: {connection_test['status']}")
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return
    
    # Get pipeline status
    print("\nGetting pipeline status...")
    try:
        status = client.get_status()
        print(f"✓ Pipeline status: {status['status']}")
        print(f"  Components: {list(status['components'].keys())}")
    except Exception as e:
        print(f"✗ Status check failed: {e}")
    
    # Example citizen report data
    report_data = {
        "photo_url": "https://example.com/mangrove_photos/incident_001.jpg",
        "latitude": 12.345678,
        "longitude": 78.901234,
        "timestamp": datetime.now().isoformat(),
        "description": "Suspected illegal mangrove cutting in the coastal area. Large trees have been removed and there are signs of recent activity. The area looks significantly different from last month.",
        "reporter_id": "citizen_001"
    }
    
    print(f"\nSubmitting citizen report...")
    print(f"Location: ({report_data['latitude']}, {report_data['longitude']})")
    print(f"Description: {report_data['description'][:100]}...")
    
    # Submit report for validation
    start_time = time.time()
    try:
        result = client.validate_report(report_data)
        processing_time = time.time() - start_time
        
        print(f"✓ Report processed successfully in {processing_time:.2f}s")
        print(f"\nValidation Results:")
        print(f"  Report ID: {result['report_id']}")
        print(f"  Confidence Score: {result['confidence_score']:.3f}")
        print(f"  Confidence Level: {result['confidence_level']}")
        print(f"  Anomaly Detected: {result['anomaly_detected']}")
        print(f"  Anomaly Score: {result['anomaly_score']:.3f}")
        print(f"  Urgency Level: {result['urgency_level']}")
        print(f"  Points Earned: {result['points_earned']}")
        print(f"  Badges: {', '.join(result['badges'])}")
        
        print(f"\nSummary:")
        print(f"  {result['summary']}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nProcessing Metadata:")
        print(f"  Model Used: {result['metadata']['model_used']}")
        print(f"  Processing Time: {result['processing_metadata']['processing_time']}s")
        print(f"  Satellite Source: {result['processing_metadata']['satellite_data_source']}")
        print(f"  Cloud Coverage: {result['processing_metadata']['satellite_cloud_coverage']:.3f}")
        
    except Exception as e:
        print(f"✗ Report processing failed: {e}")
    
    # Get statistics
    print(f"\nGetting processing statistics...")
    try:
        stats = client.get_statistics()
        print(f"✓ Statistics retrieved")
        print(f"  Total Reports: {stats['statistics']['total_reports_processed']}")
        print(f"  Success Rate: {stats['statistics']['success_rate']:.1%}")
        print(f"  Average Processing Time: {stats['statistics']['average_processing_time']:.2f}s")
    except Exception as e:
        print(f"✗ Statistics retrieval failed: {e}")


def example_batch_processing():
    """Example of batch processing multiple reports."""
    
    client = MangroveWatchClient("http://localhost:8000")
    
    # Multiple citizen reports
    reports = [
        {
            "photo_url": "https://example.com/mangrove_photos/incident_002.jpg",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "timestamp": datetime.now().isoformat(),
            "description": "Large area of mangroves appears to have been cleared. Heavy machinery tracks visible.",
            "reporter_id": "citizen_002"
        },
        {
            "photo_url": "https://example.com/mangrove_photos/incident_003.jpg",
            "latitude": 12.3567,
            "longitude": 78.9123,
            "timestamp": datetime.now().isoformat(),
            "description": "Suspicious activity near mangrove area. People with tools seen entering the forest.",
            "reporter_id": "citizen_003"
        },
        {
            "photo_url": None,  # No photo available
            "latitude": 12.3678,
            "longitude": 78.9234,
            "timestamp": datetime.now().isoformat(),
            "description": "Heard chainsaw sounds from mangrove area. Concerned about illegal logging.",
            "reporter_id": "citizen_004"
        }
    ]
    
    print("Processing batch of citizen reports...")
    
    results = []
    for i, report in enumerate(reports, 1):
        print(f"\nProcessing report {i}/{len(reports)}...")
        try:
            result = client.validate_report(report)
            results.append(result)
            
            print(f"  ✓ Confidence: {result['confidence_score']:.3f}")
            print(f"  ✓ Anomaly: {result['anomaly_detected']}")
            print(f"  ✓ Urgency: {result['urgency_level']}")
            print(f"  ✓ Points: {result['points_earned']}")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results.append(None)
    
    # Summary
    successful_reports = [r for r in results if r is not None]
    anomalies_detected = sum(1 for r in successful_reports if r['anomaly_detected'])
    total_points = sum(r['points_earned'] for r in successful_reports)
    
    print(f"\nBatch Processing Summary:")
    print(f"  Total Reports: {len(reports)}")
    print(f"  Successful: {len(successful_reports)}")
    print(f"  Anomalies Detected: {anomalies_detected}")
    print(f"  Total Points Awarded: {total_points}")
    
    if successful_reports:
        avg_confidence = sum(r['confidence_score'] for r in successful_reports) / len(successful_reports)
        print(f"  Average Confidence: {avg_confidence:.3f}")


def example_gamification_integration():
    """Example of gamification features integration."""
    
    client = MangroveWatchClient("http://localhost:8000")
    
    # Simulate a user's reporting activity
    user_id = "active_citizen_001"
    
    print(f"Simulating gamification for user: {user_id}")
    
    # Multiple reports from the same user
    user_reports = [
        {
            "photo_url": "https://example.com/user_photos/report_001.jpg",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "timestamp": datetime.now().isoformat(),
            "description": "First report - noticed some mangrove damage",
            "reporter_id": user_id
        },
        {
            "photo_url": "https://example.com/user_photos/report_002.jpg",
            "latitude": 12.3567,
            "longitude": 78.9123,
            "timestamp": datetime.now().isoformat(),
            "description": "Second report - confirmed illegal activity",
            "reporter_id": user_id
        },
        {
            "photo_url": "https://example.com/user_photos/report_003.jpg",
            "latitude": 12.3678,
            "longitude": 78.9234,
            "timestamp": datetime.now().isoformat(),
            "description": "Third report - high-quality evidence",
            "reporter_id": user_id
        }
    ]
    
    total_points = 0
    all_badges = set()
    
    for i, report in enumerate(user_reports, 1):
        print(f"\nProcessing user report {i}...")
        try:
            result = client.validate_report(report)
            
            points = result['points_earned']
            badges = result['badges']
            
            total_points += points
            all_badges.update(badges)
            
            print(f"  Points earned: {points}")
            print(f"  New badges: {', '.join(badges)}")
            print(f"  Confidence: {result['confidence_score']:.3f}")
            
        except Exception as e:
            print(f"  Failed: {e}")
    
    print(f"\nGamification Summary for {user_id}:")
    print(f"  Total Points: {total_points}")
    print(f"  All Badges: {', '.join(sorted(all_badges))}")
    
    # Calculate level based on points
    if total_points >= 500:
        level = "Master"
    elif total_points >= 300:
        level = "Expert"
    elif total_points >= 150:
        level = "Detector"
    elif total_points >= 50:
        level = "Explorer"
    else:
        level = "Beginner"
    
    print(f"  Current Level: {level}")
    print(f"  Progress: {total_points} points")


def example_error_handling():
    """Example of error handling and edge cases."""
    
    client = MangroveWatchClient("http://localhost:8000")
    
    print("Testing error handling and edge cases...")
    
    # Test cases with potential issues
    test_cases = [
        {
            "name": "Invalid coordinates",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "latitude": 100.0,  # Invalid latitude
                "longitude": 78.9012,
                "timestamp": datetime.now().isoformat(),
                "description": "Test report",
                "reporter_id": "test_user"
            }
        },
        {
            "name": "Missing required fields",
            "data": {
                "latitude": 12.3456,
                "longitude": 78.9012,
                # Missing timestamp and reporter_id
            }
        },
        {
            "name": "Invalid timestamp",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "latitude": 12.3456,
                "longitude": 78.9012,
                "timestamp": "invalid_timestamp",
                "description": "Test report",
                "reporter_id": "test_user"
            }
        },
        {
            "name": "Invalid photo URL",
            "data": {
                "photo_url": "not_a_valid_url",
                "latitude": 12.3456,
                "longitude": 78.9012,
                "timestamp": datetime.now().isoformat(),
                "description": "Test report",
                "reporter_id": "test_user"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            result = client.validate_report(test_case['data'])
            print(f"  ✓ Unexpected success")
        except Exception as e:
            print(f"  ✓ Expected error: {str(e)[:100]}...")


if __name__ == "__main__":
    print("Community Mangrove Watch - Integration Examples")
    print("=" * 50)
    
    # Run examples
    try:
        example_citizen_report()
        print("\n" + "=" * 50)
        
        example_batch_processing()
        print("\n" + "=" * 50)
        
        example_gamification_integration()
        print("\n" + "=" * 50)
        
        example_error_handling()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nExamples failed: {e}")
    
    print("\nIntegration examples completed!")
