import os
import httpx  # Import httpx directly
from groq import Groq
from typing import BinaryIO

class AudioTranscriptionService:
    """Service for transcribing audio files using Groq Whisper model."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the transcription service.
        If api_key is not provided, it will look for GROQ_API_KEY in environment variables.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required")
            
        # FIX: Manually initialize http_client to bypass the 'proxies' argument bug
        # found in older groq versions running with new httpx versions.
        self.client = Groq(
            api_key=self.api_key,
            http_client=httpx.Client()
        )
        self.model = "whisper-large-v3"
    
    def transcribe_audio(self, audio_file: BinaryIO, filename: str) -> str:
        """
        Transcribe audio file using Groq Whisper model.
        """
        try:
            # Ensure the file pointer is at the start
            audio_file.seek(0)
            
            # Read file content
            file_content = audio_file.read()
            
            # API Call
            transcription = self.client.audio.transcriptions.create(
                file=(filename, file_content),
                model=self.model,
                response_format="text"
            )
            
            return transcription
            
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise e
    
    def save_transcription(self, transcription: str, output_path: str) -> str:
        """Save transcription to a text file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcription)
            return output_path
        except IOError as e:
            print(f"Failed to save transcription file: {e}")
            raise