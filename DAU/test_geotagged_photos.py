#!/usr/bin/env python3
"""
Test script for geotagged photo functionality.
Demonstrates how the system now requires geotagged photos and extracts coordinates automatically.
"""

import requests
import json
from datetime import datetime

def test_geotagged_photo_api():
    """Test the new geotagged photo API functionality."""
    
    base_url = "http://localhost:8000"
    
    print("📸 Testing Geotagged Photo API")
    print("=" * 50)
    
    # Test 1: Valid geotagged photo (this would work with a real geotagged photo)
    print("\n1. Testing with geotagged photo (expected to work):")
    
    valid_report = {
        "photo_url": "http://localhost:8080/M1.jpg",  # This should be a geotagged photo
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Testing with geotagged photo - coordinates will be extracted automatically",
        "reporter_id": "test_user_001"
    }
    
    print(f"Request data: {json.dumps(valid_report, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=valid_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Report ID: {result.get('report_id', 'N/A')}")
            print(f"Coordinates Source: {result.get('processing_metadata', {}).get('coordinates_source', 'N/A')}")
            print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"Anomaly Detected: {result.get('anomaly_detected', 'N/A')}")
            print(f"Urgency Level: {result.get('urgency_level', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Non-geotagged photo (should fail)
    print("\n2. Testing with non-geotagged photo (expected to fail):")
    
    invalid_report = {
        "photo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",  # Non-geotagged
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Testing with non-geotagged photo - should fail",
        "reporter_id": "test_user_002"
    }
    
    print(f"Request data: {json.dumps(invalid_report, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=invalid_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ SUCCESS! (Expected error)")
            print(f"Error: {response.text}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Missing photo URL (should fail)
    print("\n3. Testing without photo URL (expected to fail):")
    
    missing_photo_report = {
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Testing without photo - should fail",
        "reporter_id": "test_user_003"
    }
    
    print(f"Request data: {json.dumps(missing_photo_report, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=missing_photo_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print("✅ SUCCESS! (Expected validation error)")
            print(f"Error: {response.text}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("📋 New API Requirements:")
    print("=" * 50)
    print("✅ photo_url: REQUIRED (must be geotagged)")
    print("✅ timestamp: REQUIRED")
    print("✅ reporter_id: REQUIRED")
    print("❌ latitude: NO LONGER NEEDED (extracted from photo)")
    print("❌ longitude: NO LONGER NEEDED (extracted from photo)")
    print("❓ description: OPTIONAL")
    
    print("\n📸 How to create geotagged photos:")
    print("1. Use a smartphone with GPS enabled")
    print("2. Take photos with location services on")
    print("3. Upload photos to your local file server")
    print("4. The system will automatically extract coordinates")
    
    print("\n🎯 Example valid request:")
    print(json.dumps({
        "photo_url": "http://localhost:8080/geotagged_photo.jpg",
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Suspicious mangrove cutting activity",
        "reporter_id": "citizen_001"
    }, indent=2))
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_geotagged_photo_api()
