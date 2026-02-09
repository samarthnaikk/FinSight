import os
import json
import asyncio
from typing import Dict, Any
from pathlib import Path
# Import the official SDK
from backboard import BackboardClient

class TranscriptProcessingService:
    """Service for processing transcripts using Backboard's persistent memory API."""
    
    STRUCTURED_OUTPUT_FORMAT = {
        "summary": "Brief summary of the transcript",
        "key_points": ["List of key points discussed"],
        "entities": {
            "people": ["Names of people mentioned"],
            "organizations": ["Organizations mentioned"],
            "dates": ["Important dates"],
            "amounts": ["Financial amounts discussed"]
        },
        "sentiment": "Overall sentiment (positive/negative/neutral)",
        "action_items": ["List of action items or next steps"],
        "topics": ["Main topics covered"]
    }
    
    def __init__(self, backboard_api_key: str):
        """Initialize the client and set model parameters."""
        # The SDK handles the URL and authentication automatically
        self.client = BackboardClient(api_key=backboard_api_key)
        self.provider = "google"
        self.model = "gemini-2.5-pro"
        
    async def generate_structured_output(self, pii_cleaned_text: str) -> Dict[str, Any]:
        """
        Generate structured output using Gemini-2.5-pro via Backboard SDK.
        """
        prompt = f"""Analyze the following transcript and extract structured information in the following JSON format:

{json.dumps(self.STRUCTURED_OUTPUT_FORMAT, indent=2)}

Transcript:
{pii_cleaned_text}

Please provide your response as valid JSON matching the format above."""

        try:
            # 1. Create an assistant (or use an existing ID)
            assistant = await self.client.create_assistant(
                name="Transcript Analyzer",
                system_prompt="You are an expert financial transcript analyst. Always return valid JSON."
            )
            
            # 2. Create a thread for this specific processing task
            thread = await self.client.create_thread(assistant.assistant_id)
            
            # 3. Send message and get response
            response = await self.client.add_message(
                thread_id=thread.thread_id,
                content=prompt,
                llm_provider=self.provider,
                model_name=self.model,
                stream=False
            )
            
            # The SDK returns a response object; the text content is in .content
            content = response.content
            
            # Clean potential markdown backticks from LLM output
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            
            return json.loads(content)
                
        except Exception as e:
            raise RuntimeError(f"Backboard SDK Error: {str(e)}")

    def remove_pii(self, text: str) -> str:
        """Pattern-based PII redaction (kept as is for efficiency)."""
        import re
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        return text

    async def process_transcript(
        self, 
        transcript_text: str,
        base_filename: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Complete async pipeline."""
        # Step 1: Remove PII
        pii_cleaned_text = self.remove_pii(transcript_text)
        
        # Save PII-cleaned text
        pii_cleaned_path = output_dir / f"{base_filename}_pii_cleaned.txt"
        with open(pii_cleaned_path, 'w', encoding='utf-8') as f:
            f.write(pii_cleaned_text)
        
        # Step 2: Generate structured output (awaiting the async call)
        structured_output = await self.generate_structured_output(pii_cleaned_text)
        
        # Step 3: Save structured output
        structured_output_path = output_dir / f"{base_filename}_structured.json"
        with open(structured_output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_output, f, indent=2, ensure_ascii=False)
        
        return {
            "pii_cleaned_path": str(pii_cleaned_path),
            "structured_output_path": str(structured_output_path),
            "structured_output": structured_output,
            "success": True
        }