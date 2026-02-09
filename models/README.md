# Audio Transcription API

This module provides an audio-to-text transcription service using Groq's Whisper large-v3 model.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Running the API

Start the FastAPI server:
```bash
cd models
python app.py
```

Or use uvicorn directly:
```bash
cd models
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### POST /transcribe
Transcribe an audio file to text.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (audio file in .wav or .mp3 format)

**Response:**
```json
{
  "message": "Transcription completed successfully",
  "transcription": "The transcribed text...",
  "output_file": "/path/to/transcription.txt",
  "filename": "audio_transcription.txt"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/audio.wav"
```

### GET /
Get API information and available endpoints.

### GET /health
Health check endpoint.

## Features

- Supports .wav and .mp3 audio formats
- Uses Groq's whisper-large-v3 model for accurate transcription
- Saves transcriptions as plain text files
- RESTful API design
- CORS enabled for cross-origin requests

## Directory Structure

```
models/
├── app.py                    # Main FastAPI application
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── README.md                # This file
└── audiotext/               # Transcription module
    ├── __init__.py
    ├── router.py            # API endpoints
    ├── service.py           # Groq Whisper service
    └── transcriptions/      # Output directory for transcriptions
```

## Notes

- All transcriptions are saved in the `audiotext/transcriptions/` directory
- The transcription output is saved exactly as returned by the Groq API
- File names are generated based on the original audio filename
