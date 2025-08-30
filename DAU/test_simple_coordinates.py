#!/usr/bin/env python3
"""
Simple test with coordinates that should work and potentially trigger anomalies.
"""

import requests
import json

def test_simple_coordinates():
    """Test simple coordinates that should work."""
    
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Simple Coordinates for Anomaly Detection")
    print("=" * 50)
    
    # Test coordinates that should work
    test_coords = [
        {"name": "Sundarbans, Bangladesh", "lat": 21.9497, "lon": 89.1833},
        {"name": "Mangrove Bay, Thailand", "lat": 8.5379, "lon": 98.3000},
        {"name": "Mangrove Forest, Malaysia", "lat": 3.1390, "lon": 101.6869},
        {"name": "Mangrove Area, Indonesia", "lat": -6.2088, "lon": 106.8456},
        {"name": "Mangrove Coast, Vietnam", "lat": 10.8231, "lon": 106.6297},
        {"name": "Mangrove Swamp, Nigeria", "lat": 6.5244, "lon": 3.3792},
        {"name": "Mangrove Forest, Kenya", "lat": -4.0435, "lon": 39.6682},
        {"name": "Mangrove Coast, Australia", "lat": -12.4634, "lon": 130.8456},
        {"name": "Mangrove Forest, India", "lat": 19.0760, "lon": 72.8777},
        {"name": "Sundarbans, India", "lat": 21.9497, "lon": 88.9000},
    ]
    
    print("\n📋 Working Coordinates for Postman Testing:")
    print("=" * 50)
    
    for i, coord in enumerate(test_coords, 1):
        print(f"\n{i}. {coord['name']}")
        print(f"   Coordinates: ({coord['lat']}, {coord['lon']})")
        print(f"   JSON for Postman:")
        print(f"   {{")
        print(f'     "photo_url": "http://localhost:8080/M1.jpg",')
        print(f'     "latitude": {coord["lat"]},')
        print(f'     "longitude": {coord["lon"]},')
        print(f'     "timestamp": "2024-01-15T10:30:00Z",')
        print(f'     "description": "Testing with {coord["name"]}",')
        print(f'     "reporter_id": "test_user_{i:03d}"')
        print(f"   }}")
    
    print("\n" + "=" * 50)
    print("🎯 Quick Test Results:")
    print("=" * 50)
    
    # Test first coordinate
    test_coord = test_coords[0]
    print(f"\nTesting: {test_coord['name']}")
    
    report_data = {
        "photo_url": "http://localhost:8080/M1.jpg",
        "latitude": test_coord['lat'],
        "longitude": test_coord['lon'],
        "timestamp": "2024-01-15T10:30:00Z",
        "description": f"Testing with {test_coord['name']}",
        "reporter_id": "test_user_001"
    }
    
    try:
        response = requests.post(
            f"{base_url}/validate-report",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Anomaly Detected: {result.get('anomaly_detected', False)}")
            print(f"   Anomaly Score: {result.get('anomaly_score', 0.0):.3f}")
            print(f"   Confidence Score: {result.get('confidence_score', 0.0):.3f}")
            print(f"   Urgency Level: {result.get('urgency_level', 'N/A')}")
            print(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_simple_coordinates()
