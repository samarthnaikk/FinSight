import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .service import AudioTranscriptionService

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(prefix="/transcribe", tags=["transcription"])

# Get API key from environment (will be checked when service is initialized)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Transcription service will be initialized on first request
transcription_service = None


def get_transcription_service():
    """Get or initialize the transcription service."""
    global transcription_service
    if transcription_service is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        transcription_service = AudioTranscriptionService(api_key=GROQ_API_KEY)
    return transcription_service

# Directory to store transcriptions
TRANSCRIPTIONS_DIR = Path(__file__).parent / "transcriptions"
TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)


@router.post("")
async def transcribe_audio(file: UploadFile = File(...)):
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
        # Get transcription service
        service = get_transcription_service()
        
        # Transcribe audio
        transcription = service.transcribe_audio(
            audio_file=file.file,
            filename=file.filename
        )
        
        # Generate output filename
        base_name = Path(file.filename).stem
        output_filename = f"{base_name}_transcription.txt"
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
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during transcription: {str(e)}"
        )
