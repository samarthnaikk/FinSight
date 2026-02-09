import os
import re
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .service import AudioTranscriptionService

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(prefix="/transcribe", tags=["transcription"])

# Directory to store transcriptions
TRANSCRIPTIONS_DIR = Path(__file__).parent / "transcriptions"
TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)


def get_transcription_service() -> AudioTranscriptionService:
    """
    Dependency injection for transcription service.
    Creates a new service instance with API key from environment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: GROQ_API_KEY not configured"
        )
    return AudioTranscriptionService(api_key=api_key)


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


@router.post("")
async def transcribe_audio(
    file: UploadFile = File(...),
    service: AudioTranscriptionService = Depends(get_transcription_service)
):
    """
    Transcribe audio file to text using Groq Whisper model.
    
    Accepts .wav or .mp3 files and returns transcription saved to a .txt file.
    """
    # Validate file format
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in [".wav", ".mp3"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .wav and .mp3 files are supported."
        )
    
    try:
        # Transcribe audio
        transcription = service.transcribe_audio(
            audio_file=file.file,
            filename=file.filename
        )
        
        # Generate output filename with sanitization
        base_name = Path(file.filename).stem
        safe_base_name = sanitize_filename(base_name)
        output_filename = f"{safe_base_name}_transcription.txt"
        output_path = TRANSCRIPTIONS_DIR / output_filename
        
        # Save transcription to file
        saved_path = service.save_transcription(
            transcription=transcription,
            output_path=str(output_path)
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Transcription completed successfully",
                "transcription": transcription,
                "output_file": str(output_path),
                "filename": output_filename
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error server-side (in production, use proper logging)
        import traceback
        traceback.print_exc()
        # Return generic error to client
        raise HTTPException(
            status_code=500,
            detail="An error occurred during transcription. Please try again."
        )
