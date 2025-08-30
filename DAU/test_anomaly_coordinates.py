#!/usr/bin/env python3
"""
Test script to find coordinates that trigger anomaly detection.
This will help identify locations where the AI model detects suspicious activity.
"""

import requests
import json
from datetime import datetime

def test_coordinates_for_anomaly():
    """Test different coordinates to find ones that trigger anomaly detection."""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Coordinates for Anomaly Detection")
    print("=" * 60)
    
    # Test coordinates - real mangrove locations around the world
    test_coordinates = [
        # Southeast Asia (major mangrove regions)
        {"name": "Sundarbans, Bangladesh", "lat": 21.9497, "lon": 89.1833},
        {"name": "Mangrove Bay, Thailand", "lat": 8.5379, "lon": 98.3000},
        {"name": "Mangrove Forest, Malaysia", "lat": 3.1390, "lon": 101.6869},
        {"name": "Mangrove Area, Indonesia", "lat": -6.2088, "lon": 106.8456},
        {"name": "Mangrove Coast, Vietnam", "lat": 10.8231, "lon": 106.6297},
        
        # South America
        {"name": "Amazon Mangroves, Brazil", "lat": -1.4557, "lon": -48.4902},
        {"name": "Mangrove Delta, Colombia", "lat": 10.9685, "lon": -74.7813},
        
        # Africa
        {"name": "Mangrove Swamp, Nigeria", "lat": 6.5244, "lon": 3.3792},
        {"name": "Mangrove Forest, Kenya", "lat": -4.0435, "lon": 39.6682},
        
        # North America
        {"name": "Everglades, Florida", "lat": 25.7617, "lon": -80.1918},
        {"name": "Mangrove Bay, Mexico", "lat": 19.4326, "lon": -99.1332},
        
        # Australia
        {"name": "Mangrove Coast, Australia", "lat": -12.4634, "lon": 130.8456},
        
        # India
        {"name": "Mangrove Forest, India", "lat": 19.0760, "lon": 72.8777},
        {"name": "Sundarbans, India", "lat": 21.9497, "lon": 88.9000},
        
        # Test edge cases
        {"name": "Equator Line", "lat": 0.0, "lon": 0.0},
        {"name": "High Latitude", "lat": 89.0, "lon": 0.0},
        {"name": "International Date Line", "lat": 0.0, "lon": 180.0},
    ]
    
    anomaly_results = []
    
    for i, coord in enumerate(test_coordinates, 1):
        print(f"\n{i}. Testing: {coord['name']}")
        print(f"   Coordinates: ({coord['lat']}, {coord['lon']})")
        
        # Test with photo
        report_data = {
            "photo_url": "http://localhost:8080/M1.jpg",
            "latitude": coord['lat'],
            "longitude": coord['lon'],
            "timestamp": "2024-01-15T10:30:00Z",
            "description": f"Testing anomaly detection at {coord['name']}",
            "reporter_id": f"test_user_{i:03d}"
        }
        
        try:
            response = requests.post(
                f"{base_url}/validate-report",
                json=report_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                anomaly_detected = result.get('anomaly_detected', False)
                anomaly_score = result.get('anomaly_score', 0.0)
                confidence_score = result.get('confidence_score', 0.0)
                
                print(f"   ✅ Success!")
                print(f"   Anomaly Detected: {anomaly_detected}")
                print(f"   Anomaly Score: {anomaly_score:.3f}")
                print(f"   Confidence Score: {confidence_score:.3f}")
                
                if anomaly_detected:
                    anomaly_results.append({
                        'name': coord['name'],
                        'latitude': coord['lat'],
                        'longitude': coord['lon'],
                        'anomaly_score': anomaly_score,
                        'confidence_score': confidence_score
                    })
                    print(f"   🚨 ANOMALY DETECTED!")
                else:
                    print(f"   ✅ No anomaly detected")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Summary of anomaly results
    print("\n" + "=" * 60)
    print("📊 ANOMALY DETECTION RESULTS SUMMARY")
    print("=" * 60)
    
    if anomaly_results:
        print(f"🎯 Found {len(anomaly_results)} coordinates with anomalies:")
        for i, result in enumerate(anomaly_results, 1):
            print(f"\n{i}. {result['name']}")
            print(f"   Coordinates: ({result['latitude']}, {result['longitude']})")
            print(f"   Anomaly Score: {result['anomaly_score']:.3f}")
            print(f"   Confidence Score: {result['confidence_score']:.3f}")
            print(f"   JSON for Postman:")
            print(f"   {{")
            print(f'     "photo_url": "http://localhost:8080/M1.jpg",')
            print(f'     "latitude": {result["latitude"]},')
            print(f'     "longitude": {result["longitude"]},')
            print(f'     "timestamp": "2024-01-15T10:30:00Z",')
            print(f'     "description": "Testing anomaly detection",')
            print(f'     "reporter_id": "test_user_anomaly_{i}"')
            print(f"   }}")
    else:
        print("❌ No anomalies detected in any coordinates")
        print("💡 This might be because:")
        print("   - The model is using random weights (not trained)")
        print("   - The mock satellite data is too similar to photos")
        print("   - The anomaly threshold is set too high")
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_coordinates_for_anomaly()
