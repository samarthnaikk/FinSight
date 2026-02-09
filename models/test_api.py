#!/usr/bin/env python3
"""
Test script for the Audio Transcription API.

This script demonstrates how to use the transcription API with sample audio files.
Note: This requires a valid GROQ_API_KEY in your .env file.
"""

import requests
import json
import os
from pathlib import Path


def test_api_endpoints():
    """Test basic API endpoints."""
    base_url = "http://localhost:8000"
    
    print("Testing API Endpoints")
    print("=" * 50)
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test health endpoint
    print("\n2. Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n" + "=" * 50)


def test_transcription(audio_file_path: str):
    """Test audio transcription endpoint."""
    base_url = "http://localhost:8000"
    
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        print("\nTo test transcription, provide a .wav or .mp3 file:")
        print(f"  python test_api.py /path/to/your/audio.wav")
        return
    
    print(f"\n3. Testing transcription with file: {audio_file_path}")
    print("=" * 50)
    
    with open(audio_file_path, "rb") as audio_file:
        files = {"file": (Path(audio_file_path).name, audio_file)}
        response = requests.post(f"{base_url}/transcribe", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nTranscription successful!")
        print(f"Output file: {result['filename']}")
        print(f"Transcription preview: {result['transcription'][:200]}...")
    else:
        print(f"Error: {response.text}")
    
    print("=" * 50)


if __name__ == "__main__":
    import sys
    
    print("\nFinSight Audio Transcription API - Test Script")
    print("=" * 50)
    print("Make sure the API server is running on http://localhost:8000")
    print("Start it with: cd models && python app.py")
    print()
    
    # Test basic endpoints
    test_api_endpoints()
    
    # Test transcription if audio file is provided
    if len(sys.argv) > 1:
        test_transcription(sys.argv[1])
    else:
        print("\nNote: To test transcription, provide an audio file:")
        print("  python test_api.py /path/to/your/audio.wav")
