# Filtertext Module

Post-processing pipeline for transcript text with PII filtering and structured output generation.

## Overview

The filtertext module provides a two-step pipeline for processing transcripts:

1. **PII Removal**: Uses local model (Phi-3-mini) or pattern-based redaction to remove personally identifiable information
2. **Structured Output Generation**: Uses Gemini-2.5-pro via Backboard API to generate structured insights

## Features

- Local PII detection and redaction (no data sent to external services for PII removal)
- Support for both model-based (Phi-3-mini) and pattern-based PII removal
- Structured output generation with predefined format
- RESTful API endpoints for easy integration
- Saves outputs exactly as returned by the LLM

## Setup

### Prerequisites

1. Python 3.8+
2. Required packages (see `models/requirements.txt`)
3. Backboard API key for structured output generation

### Configuration

Add the following to your `.env` file in the `models/` directory:

```env
BACKBOARD_API_KEY=your_backboard_api_key_here
```

### Installation

```bash
cd models
pip install -r requirements.txt
```

## API Endpoints

### POST /filtertext/process

Process transcript text through the complete pipeline.

**Request Body:**
```json
{
  "text": "Your transcript text here...",
  "filename": "optional_base_filename"
}
```

**Response:**
```json
{
  "message": "Transcript processed successfully",
  "pii_cleaned_file": "path/to/pii_cleaned.txt",
  "structured_output_file": "path/to/structured.json",
  "structured_output": {
    "summary": "Brief summary...",
    "key_points": ["point1", "point2"],
    "entities": {...},
    "sentiment": "neutral",
    "action_items": [...],
    "topics": [...]
  }
}
```

### POST /filtertext/process-file

Process an existing transcript file from the `audiotext/transcriptions/` directory.

**Request Body:**
```json
{
  "transcript_filename": "audio_transcription.txt"
}
```

**Response:**
```json
{
  "message": "Transcript file processed successfully",
  "source_file": "path/to/source.txt",
  "pii_cleaned_file": "path/to/pii_cleaned.txt",
  "structured_output_file": "path/to/structured.json",
  "structured_output": {...}
}
```

### GET /filtertext/status

Get the status of the transcript processing service.

**Response:**
```json
{
  "service": "Transcript Post-Processing",
  "status": "operational",
  "backboard_api_configured": true,
  "endpoints": {...},
  "pipeline": [
    "1. PII Removal (Local Model: Phi-3-mini)",
    "2. Structured Output Generation (Gemini-2.5-pro via Backboard)"
  ]
}
```

## PII Removal

### Pattern-Based Redaction (Default)

The service uses enhanced pattern-based redaction by default, which is fast and doesn't require model downloads:

- Email addresses
- Phone numbers (multiple formats)
- SSN (Social Security Numbers)
- Credit card numbers
- Physical addresses
- ZIP codes
- Names (in common contexts)

### Model-Based Redaction (Optional)

To use the Phi-3-mini model for more accurate PII detection:

1. Ensure you have sufficient RAM (8GB+) and disk space (~7GB for model)
2. GPU is recommended for faster processing
3. Set `use_model=True` in the service initialization

**Note:** The model will be downloaded automatically on first use.

## Structured Output Format

The LLM generates output in the following structure:

```json
{
  "summary": "Brief summary of the transcript",
  "key_points": [
    "List of key points discussed"
  ],
  "entities": {
    "people": ["Names of people mentioned"],
    "organizations": ["Organizations mentioned"],
    "dates": ["Important dates"],
    "amounts": ["Financial amounts discussed"]
  },
  "sentiment": "Overall sentiment (positive/negative/neutral)",
  "action_items": [
    "List of action items or next steps"
  ],
  "topics": [
    "Main topics covered"
  ]
}
```

**Important:** The structured output is saved exactly as returned by the LLM without modification.

## Directory Structure

```
filtertext/
├── __init__.py              # Module initialization
├── router.py                # FastAPI route definitions
├── service.py               # Core processing logic
├── processed_outputs/       # Output directory for processed files
└── README.md               # This file
```

## Usage Examples

### Using the API

```bash
# Process transcript text
curl -X POST "http://localhost:8000/filtertext/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your transcript text here...",
    "filename": "my_transcript"
  }'

# Process existing transcript file
curl -X POST "http://localhost:8000/filtertext/process-file" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_filename": "audio_transcription.txt"
  }'

# Check service status
curl "http://localhost:8000/filtertext/status"
```

### Using the Service Directly

```python
from filtertext.service import TranscriptProcessingService
from pathlib import Path

# Initialize service
service = TranscriptProcessingService(
    backboard_api_key="your_api_key"
)

# Process transcript
transcript_text = "Your transcript text..."
result = service.process_transcript(
    transcript_text=transcript_text,
    base_filename="my_transcript",
    output_dir=Path("./outputs")
)

print(f"PII cleaned: {result['pii_cleaned_path']}")
print(f"Structured: {result['structured_output_path']}")
```

## Testing

Run the test suite:

```bash
# Test PII redaction
python test_pii_redaction.py

# Test integration (with mocked Backboard API)
python test_integration.py

# Test API endpoints (requires running server)
python test_filtertext.py
```

## Notes

- All PII removal is performed locally (no external API calls)
- Structured output generation requires internet access to Backboard API
- Output files are saved in `filtertext/processed_outputs/` directory
- The service maintains separation between PII removal and structured generation
- Outputs are saved exactly as returned, without modification

## Security Considerations

- PII is redacted locally before sending to any external service
- API keys should be stored securely in environment variables
- Output files may contain sensitive information (even after PII removal)
- Ensure proper access controls on the `processed_outputs/` directory

## Troubleshooting

### "BACKBOARD_API_KEY not configured"

Make sure you have added `BACKBOARD_API_KEY` to your `.env` file in the `models/` directory.

### "Failed to call Backboard API"

- Check your internet connection
- Verify your Backboard API key is valid
- Check if the Backboard API endpoint is accessible

### Model Loading Issues

If using model-based PII removal:
- Ensure you have sufficient disk space (~7GB)
- Check if you have enough RAM (8GB+ recommended)
- Consider using pattern-based redaction instead (set `use_model=False`)

## License

MIT License - See root LICENSE file for details.
