#!/usr/bin/env python3
"""
Simple test script to verify the API is working correctly.
This will help us understand the exact format needed.
"""

import requests
import json
from datetime import datetime

def test_api():
    """Test the API endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("🌿 Testing Community Mangrove Watch API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Validate report (correct format)
    print("\n3. Testing validate report (correct format)...")
    
    # This is the CORRECT format
    report_data = {
        "photo_url": "https://example.com/mangrove_photo.jpg",
        "latitude": 12.345678,
        "longitude": 78.901234,
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Suspicious mangrove cutting activity detected.",
        "reporter_id": "test_user_001"
    }
    
    print(f"Sending data: {json.dumps(report_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"Anomaly Detected: {result.get('anomaly_detected', 'N/A')}")
            print(f"Urgency Level: {result.get('urgency_level', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Validate report (no photo)
    print("\n4. Testing validate report (no photo)...")
    
    report_data_no_photo = {
        "latitude": 12.345678,
        "longitude": 78.901234,
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Report without photo - heard chainsaw sounds",
        "reporter_id": "test_user_002"
    }
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=report_data_no_photo,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"Anomaly Detected: {result.get('anomaly_detected', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Error case - invalid coordinates
    print("\n5. Testing error case (invalid coordinates)...")
    
    invalid_report = {
        "photo_url": "https://example.com/photo.jpg",
        "latitude": 100.0,  # Invalid latitude
        "longitude": 78.901234,
        "timestamp": "2024-01-15T10:30:00Z",
        "description": "Test with invalid coordinates",
        "reporter_id": "test_user_003"
    }
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=invalid_report,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ SUCCESS! (Expected error)")
            print(f"Error: {response.json()}")
        else:
            print(f"❌ Unexpected status: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

if __name__ == "__main__":
    test_api()
