"""
API routes for transcript post-processing.
"""

import os
import re
import traceback
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure we import the updated service
from .service import TranscriptProcessingService

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(prefix="/filtertext", tags=["transcript-processing"])

# Directory to store processed outputs
PROCESSED_OUTPUTS_DIR = Path(__file__).parent / "processed_outputs"
PROCESSED_OUTPUTS_DIR.mkdir(exist_ok=True)

# Directory where transcriptions are stored (assuming standard project structure)
# Adjust this path if your audiotext folder is located elsewhere relative to filtertext
TRANSCRIPTIONS_DIR = Path(__file__).parent.parent / "audiotext" / "transcriptions"


class TranscriptProcessRequest(BaseModel):
    """Request model for processing transcript text directly."""
    text: str
    filename: Optional[str] = "transcript"


class TranscriptFileProcessRequest(BaseModel):
    """Request model for processing an existing transcript file."""
    transcript_filename: str


def get_processing_service():
    """
    Dependency injection for transcript processing service.
    """
    api_key = os.getenv("BACKBOARD_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: BACKBOARD_API_KEY not configured"
        )
    return TranscriptProcessingService(backboard_api_key=api_key)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    base_name = Path(filename).name
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', base_name)
    return sanitized


@router.post("/process")
async def process_transcript_text(
    request: TranscriptProcessRequest,
    service: TranscriptProcessingService = Depends(get_processing_service)
):
    """
    Process transcript text through the complete pipeline.
    """
    try:
        safe_filename = sanitize_filename(request.filename)
        
        # CHANGED: Added 'await' because service methods are now async
        result = await service.process_transcript(
            transcript_text=request.text,
            base_filename=safe_filename,
            output_dir=PROCESSED_OUTPUTS_DIR
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Transcript processed successfully",
                "files": {
                    "pii_cleaned": result["pii_cleaned_path"],
                    "structured_output": result["structured_output_path"]
                },
                "data": result["structured_output"]
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during processing: {str(e)}"
        )


@router.post("/process-file")
async def process_transcript_file(
    request: TranscriptFileProcessRequest,
    service: TranscriptProcessingService = Depends(get_processing_service)
):
    """
    Process an existing transcript file from the audiotext/transcriptions directory.
    """
    try:
        safe_filename = sanitize_filename(request.transcript_filename)
        transcript_path = TRANSCRIPTIONS_DIR / safe_filename
        
        if not transcript_path.exists():
            # Try looking in the local directory if not found in ../audiotext/transcriptions
            # This is helpful during testing
            local_path = Path(safe_filename)
            if local_path.exists():
                transcript_path = local_path
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Transcript file not found at: {transcript_path}"
                )
        
        # Read the transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        # Generate base filename
        base_filename = safe_filename.replace('_transcription.txt', '').replace('.txt', '')
        
        # CHANGED: Added 'await' here as well
        result = await service.process_transcript(
            transcript_text=transcript_text,
            base_filename=base_filename,
            output_dir=PROCESSED_OUTPUTS_DIR
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File processed successfully",
                "source": str(transcript_path),
                "files": {
                    "pii_cleaned": result["pii_cleaned_path"],
                    "structured_output": result["structured_output_path"]
                },
                "data": result["structured_output"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during file processing: {str(e)}"
        )


@router.get("/status")
async def get_processing_status():
    """Get status of the transcript processing service."""
    return {
        "service": "Transcript Post-Processing",
        "status": "operational",
        "configuration": {
            "backboard_api": bool(os.getenv("BACKBOARD_API_KEY")),
            "output_dir": str(PROCESSED_OUTPUTS_DIR),
            "input_dir": str(TRANSCRIPTIONS_DIR)
        }
    }