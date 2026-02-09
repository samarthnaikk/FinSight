import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from audiotext.router import router as transcription_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FinSight Audio Transcription API",
    description="API for transcribing audio files using Groq Whisper model",
    version="1.0.0"
)

# Get allowed origins from environment or default to localhost
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(transcription_router)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "FinSight Audio Transcription API",
        "version": "1.0.0",
        "endpoints": {
            "transcribe": "/transcribe"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
