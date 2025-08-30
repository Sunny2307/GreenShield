#!/usr/bin/env python3
"""
Simple test script to demonstrate the complete data flow.
Run this to see how data flows through the pipeline without starting the API server.
"""

import json
import time
from datetime import datetime
from src.pipeline.mangrove_pipeline import MangrovePipeline

def test_complete_pipeline():
    """Test the complete pipeline with sample data."""
    
    print("🌿 Community Mangrove Watch - Pipeline Test")
    print("=" * 50)
    
    # Initialize the pipeline
    print("Initializing pipeline...")
    pipeline = MangrovePipeline()
    
    # Sample citizen report (INPUT FORMAT)
    print("\n📥 INPUT DATA FORMAT:")
    report_data = {
        "photo_url": "https://example.com/mangrove_incident.jpg",
        "latitude": 12.345678,
        "longitude": 78.901234,
        "timestamp": datetime.now().isoformat(),
        "description": "Suspicious mangrove cutting activity detected. Large trees have been removed and there are signs of recent heavy machinery activity.",
        "reporter_id": "citizen_001"
    }
    
    print(json.dumps(report_data, indent=2))
    
    # Process through pipeline
    print("\n🔄 PROCESSING THROUGH PIPELINE...")
    print("Step 1: Preprocessing report data...")
    print("Step 2: Fetching satellite imagery...")
    print("Step 3: Running AI validation...")
    print("Step 4: Postprocessing results...")
    
    start_time = time.time()
    
    try:
        # This is where the magic happens!
        result = pipeline.process_report(report_data)
        processing_time = time.time() - start_time
        
        print(f"\n✅ PROCESSING COMPLETED in {processing_time:.2f} seconds")
        
        # OUTPUT FORMAT
        print("\n📤 OUTPUT DATA FORMAT:")
        print(json.dumps(result, indent=2))
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"  Confidence Score: {result['confidence_score']:.3f}")
        print(f"  Confidence Level: {result['confidence_level']}")
        print(f"  Anomaly Detected: {result['anomaly_detected']}")
        print(f"  Urgency Level: {result['urgency_level']}")
        print(f"  Points Earned: {result['points_earned']}")
        print(f"  Badges: {', '.join(result['badges'])}")
        
        print(f"\n📝 Summary: {result['summary']}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("This is expected if satellite APIs are not configured.")
        print("The system works for testing without satellite data.")

def test_input_validation():
    """Test input validation with various scenarios."""
    
    print("\n" + "=" * 50)
    print("🧪 INPUT VALIDATION TESTS")
    print("=" * 50)
    
    pipeline = MangrovePipeline()
    
    test_cases = [
        {
            "name": "Valid Report",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "latitude": 12.345,
                "longitude": 78.901,
                "timestamp": datetime.now().isoformat(),
                "description": "Test report",
                "reporter_id": "user123"
            },
            "should_pass": True
        },
        {
            "name": "Invalid Latitude",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "latitude": 100.0,  # Invalid
                "longitude": 78.901,
                "timestamp": datetime.now().isoformat(),
                "description": "Test report",
                "reporter_id": "user123"
            },
            "should_pass": False
        },
        {
            "name": "Missing Required Fields",
            "data": {
                "latitude": 12.345,
                "longitude": 78.901,
                # Missing timestamp and reporter_id
            },
            "should_pass": False
        },
        {
            "name": "No Photo Report",
            "data": {
                "latitude": 12.345,
                "longitude": 78.901,
                "timestamp": datetime.now().isoformat(),
                "description": "Report without photo",
                "reporter_id": "user123"
            },
            "should_pass": True
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            validation = pipeline.validate_input(test_case['data'])
            if validation['valid'] == test_case['should_pass']:
                print(f"  ✅ PASS - Expected: {test_case['should_pass']}, Got: {validation['valid']}")
            else:
                print(f"  ❌ FAIL - Expected: {test_case['should_pass']}, Got: {validation['valid']}")
            
            if not validation['valid'] and validation['errors']:
                print(f"  Errors: {validation['errors']}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

def test_pipeline_status():
    """Test pipeline status and health."""
    
    print("\n" + "=" * 50)
    print("🏥 PIPELINE STATUS TEST")
    print("=" * 50)
    
    pipeline = MangrovePipeline()
    
    try:
        status = pipeline.get_pipeline_status()
        print("Pipeline Status:")
        print(json.dumps(status, indent=2))
        
        if status['status'] == 'healthy':
            print("✅ Pipeline is healthy and ready!")
        else:
            print("⚠️  Pipeline has issues")
            
    except Exception as e:
        print(f"❌ Error getting status: {e}")

if __name__ == "__main__":
    print("Starting Community Mangrove Watch Pipeline Tests...")
    
    # Test 1: Complete pipeline flow
    test_complete_pipeline()
    
    # Test 2: Input validation
    test_input_validation()
    
    # Test 3: Pipeline status
    test_pipeline_status()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nTo run the API server:")
    print("python -m uvicorn src.api.main:app --host localhost --port 8000 --reload")
    print("\nThen visit: http://localhost:8000/docs")
