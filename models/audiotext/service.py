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
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        # whisper-large-v3-turbo is faster and cheaper, whisper-large-v3 is more accurate for multilingual
        self.model = "whisper-large-v3"
    
    def transcribe_audio(self, audio_file: BinaryIO, filename: str) -> str:
        """
        Transcribe audio file using Groq Whisper model.
        
        Args:
            audio_file: Binary file object of the audio
            filename: Name of the audio file (used to determine format)
            
        Returns:
            The transcription text
        """
        # It's better to pass the tuple (filename, file_content) 
        # or the file handle directly. The SDK handles the multipart encoding.
        try:
            # Ensure the file pointer is at the start
            audio_file.seek(0)
            
            # Transcription call
            transcription = self.client.audio.transcriptions.create(
                file=(filename, audio_file.read()), # Pass filename and bytes
                model=self.model,
                response_format="text", # Returns raw text as a string
                # Optional parameters:
                # language="en", 
                # temperature=0.0,
            )
            return transcription
            
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise e
    
    def save_transcription(self, transcription: str, output_path: str) -> str:
        """Save transcription to a text file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        return output_path