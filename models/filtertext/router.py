"""
API routes for transcript post-processing.

Provides endpoints for:
1. Processing existing transcripts through PII filtering and structured output generation
2. Loading and processing transcript files
"""

import os
import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from .service import TranscriptProcessingService

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(prefix="/filtertext", tags=["transcript-processing"])

# Directory to store processed outputs
PROCESSED_OUTPUTS_DIR = Path(__file__).parent / "processed_outputs"
PROCESSED_OUTPUTS_DIR.mkdir(exist_ok=True)

# Directory where transcriptions are stored (from audiotext module)
TRANSCRIPTIONS_DIR = Path(__file__).parent.parent / "audiotext" / "transcriptions"


class TranscriptProcessRequest(BaseModel):
    """Request model for processing transcript text directly."""
    text: str
    filename: Optional[str] = "transcript"


class TranscriptFileProcessRequest(BaseModel):
    """Request model for processing an existing transcript file."""
    transcript_filename: str


def get_processing_service() -> TranscriptProcessingService:
    """
    Dependency injection for transcript processing service.
    Creates a new service instance with API key from environment.
    """
    api_key = os.getenv("BACKBOARD_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: BACKBOARD_API_KEY not configured"
        )
    return TranscriptProcessingService(backboard_api_key=api_key)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    Removes directory separators and keeps only safe characters.
    """
    # Get just the filename without path
    base_name = Path(filename).name
    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', base_name)
    return sanitized


@router.post("/process")
async def process_transcript_text(
    request: TranscriptProcessRequest,
    service: TranscriptProcessingService = Depends(get_processing_service)
):
    """
    Process transcript text through the complete pipeline:
    1. Remove PII using local model
    2. Generate structured output using Gemini-2.5-pro via Backboard
    3. Save both outputs
    
    Args:
        request: TranscriptProcessRequest with text and optional filename
        
    Returns:
        JSON response with processing results and file paths
    """
    try:
        # Sanitize filename
        safe_filename = sanitize_filename(request.filename)
        
        # Process the transcript
        result = service.process_transcript(
            transcript_text=request.text,
            base_filename=safe_filename,
            output_dir=PROCESSED_OUTPUTS_DIR
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Transcript processed successfully",
                "pii_cleaned_file": result["pii_cleaned_path"],
                "structured_output_file": result["structured_output_path"],
                "structured_output": result["structured_output"]
            }
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during transcript processing: {str(e)}"
        )


@router.post("/process-file")
async def process_transcript_file(
    request: TranscriptFileProcessRequest,
    service: TranscriptProcessingService = Depends(get_processing_service)
):
    """
    Process an existing transcript file from the audiotext/transcriptions directory.
    
    This endpoint:
    1. Loads the specified transcript file
    2. Removes PII using local model
    3. Generates structured output using Gemini-2.5-pro via Backboard
    4. Saves both outputs
    
    Args:
        request: TranscriptFileProcessRequest with transcript filename
        
    Returns:
        JSON response with processing results and file paths
    """
    try:
        # Sanitize and validate filename
        safe_filename = sanitize_filename(request.transcript_filename)
        transcript_path = TRANSCRIPTIONS_DIR / safe_filename
        
        # Check if file exists
        if not transcript_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcript file not found: {safe_filename}"
            )
        
        # Read the transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        # Generate base filename for outputs (remove _transcription.txt suffix if present)
        base_filename = safe_filename.replace('_transcription.txt', '').replace('.txt', '')
        
        # Process the transcript
        result = service.process_transcript(
            transcript_text=transcript_text,
            base_filename=base_filename,
            output_dir=PROCESSED_OUTPUTS_DIR
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Transcript file processed successfully",
                "source_file": str(transcript_path),
                "pii_cleaned_file": result["pii_cleaned_path"],
                "structured_output_file": result["structured_output_path"],
                "structured_output": result["structured_output"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during transcript file processing: {str(e)}"
        )


@router.get("/status")
async def get_processing_status():
    """
    Get status of the transcript processing service.
    
    Returns information about available endpoints and configuration.
    """
    backboard_configured = bool(os.getenv("BACKBOARD_API_KEY"))
    
    return {
        "service": "Transcript Post-Processing",
        "status": "operational",
        "backboard_api_configured": backboard_configured,
        "endpoints": {
            "process": "/filtertext/process - Process transcript text directly",
            "process_file": "/filtertext/process-file - Process existing transcript file"
        },
        "pipeline": [
            "1. PII Removal (Local Model: Phi-3-mini)",
            "2. Structured Output Generation (Gemini-2.5-pro via Backboard)"
        ]
    }
