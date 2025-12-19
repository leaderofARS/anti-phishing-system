"""
Test script for Anti-Phishing API
Run this after starting the backend server
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Test health check"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_analyze_safe():
    """Test analyzing a safe URL"""
    print("\n=== Testing Safe URL Analysis ===")
    data = {
        "url": "https://www.google.com",
        "context": "test"
    }
    response = requests.post(f"{API_URL}/api/analyze", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"URL: {result['url']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Scan Time: {result['scan_time']:.2f}s")
    print(f"Recommendations: {result['recommendations']}")

def test_analyze_suspicious():
    """Test analyzing a suspicious URL"""
    print("\n=== Testing Suspicious URL Analysis ===")
    data = {
        "url": "http://192.168.1.1/login-verify-account-suspended",
        "context": "test"
    }
    response = requests.post(f"{API_URL}/api/analyze", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"URL: {result['url']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Allow Access: {result['allow_access']}")

def test_quick_check():
    """Test quick check endpoint"""
    print("\n=== Testing Quick Check ===")
    url = "https://www.github.com"
    response = requests.get(f"{API_URL}/api/check/{url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_report():
    """Test reporting phishing"""
    print("\n=== Testing Report Phishing ===")
    data = {
        "url": "http://phishing-site.com",
        "reason": "Suspicious login page",
        "user_id": "test_user"
    }
    response = requests.post(f"{API_URL}/api/report", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_stats():
    """Test statistics endpoint"""
    print("\n=== Testing Statistics ===")
    response = requests.get(f"{API_URL}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Anti-Phishing API Test Suite")
    print("=" * 60)
    
    try:
        test_root()
        test_health()
        test_analyze_safe()
        test_analyze_suspicious()
        test_quick_check()
        test_report()
        test_stats()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
