import os
from pathlib import Path
from groq import Groq
from typing import BinaryIO


class AudioTranscriptionService:
    """Service for transcribing audio files using Groq Whisper model."""
    
    def __init__(self, api_key: str):
        """Initialize the transcription service with Groq API key."""
        self.client = Groq(api_key=api_key)
        self.model = "whisper-large-v3"
    
    def transcribe_audio(self, audio_file: BinaryIO, filename: str) -> str:
        """
        Transcribe audio file using Groq Whisper model.
        
        Args:
            audio_file: Binary file object of the audio
            filename: Name of the audio file
            
        Returns:
            Transcription text as returned by the model
        """
        # Read file content and reset stream for potential retries
        file_content = audio_file.read()
        audio_file.seek(0)
        
        transcription = self.client.audio.transcriptions.create(
            file=(filename, file_content),
            model=self.model,
            response_format="text"
        )
        return transcription
    
    def save_transcription(self, transcription: str, output_path: str) -> str:
        """
        Save transcription to a text file.
        
        Args:
            transcription: The transcription text to save
            output_path: Path where the transcription should be saved
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        return output_path
