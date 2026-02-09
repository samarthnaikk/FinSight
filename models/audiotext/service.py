import os
from groq import Groq
from typing import BinaryIO

class AudioTranscriptionService:
    """Service for transcribing audio files using Groq Whisper model."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the transcription service.
        If api_key is not provided, it will look for GROQ_API_KEY in environment variables.
        """
        # Ensure we capture the API key correctly
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required")
            
        self.client = Groq(api_key=self.api_key)
        self.model = "whisper-large-v3"
    
    def transcribe_audio(self, audio_file: BinaryIO, filename: str) -> str:
        """
        Transcribe audio file using Groq Whisper model.
        
        Args:
            audio_file: Binary file object of the audio (file-like object)
            filename: Name of the audio file (used to determine format)
            
        Returns:
            The transcription text
        """
        try:
            # Ensure the file pointer is at the start
            audio_file.seek(0)
            
            # Read the file content once
            file_content = audio_file.read()
            
            # API Call
            # We pass the tuple (filename, file_content) to ensure Groq knows the file extension
            transcription = self.client.audio.transcriptions.create(
                file=(filename, file_content),
                model=self.model,
                response_format="text" # Returns raw string
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