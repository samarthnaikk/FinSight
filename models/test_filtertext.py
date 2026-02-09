#!/usr/bin/env python3
"""
Test script for the filtertext API endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_root():
    """Test root endpoint."""
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Message: {result.get('message')}")
        print(f"   Endpoints: {json.dumps(result.get('endpoints'), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_filtertext_status():
    """Test filtertext status endpoint."""
    print("\n3. Testing filtertext status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/filtertext/status")
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Service: {result.get('service')}")
        print(f"   Backboard API Configured: {result.get('backboard_api_configured')}")
        print(f"   Pipeline: {json.dumps(result.get('pipeline'), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_process_text():
    """Test process endpoint with sample text."""
    print("\n4. Testing process endpoint with sample text...")
    try:
        sample_text = """
        Hello, my name is John Doe and my email is john.doe@example.com.
        I can be reached at 555-123-4567. My address is 123 Main Street, Springfield.
        We discussed financial planning and investment strategies for 2024.
        The key action items are:
        1. Review portfolio allocation
        2. Schedule follow-up meeting next month
        3. Prepare quarterly report
        """
        
        payload = {
            "text": sample_text,
            "filename": "test_transcript"
        }
        
        response = requests.post(
            f"{BASE_URL}/filtertext/process",
            json=payload,
            timeout=120
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Message: {result.get('message')}")
            print(f"   PII Cleaned File: {result.get('pii_cleaned_file')}")
            print(f"   Structured Output File: {result.get('structured_output_file')}")
            if result.get('structured_output'):
                print(f"   Structured Output Preview:")
                print(f"     Summary: {result['structured_output'].get('summary', 'N/A')[:100]}...")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print("=" * 70)
    print("FinSight Filtertext API Test Suite")
    print("=" * 70)
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Start it with: cd models && python app.py")
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Filtertext Status", test_filtertext_status()))
    
    # Only test processing if basic endpoints work
    if all(r[1] for r in results):
        print("\n" + "=" * 70)
        print("Basic endpoints working. Testing processing endpoint...")
        print("=" * 70)
        results.append(("Process Text", test_process_text()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("=" * 70)
    
    # Return exit code
    return 0 if all(r[1] for r in results) else 1

if __name__ == "__main__":
    exit(main())
