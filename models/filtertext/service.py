import os
import json
import asyncio
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import the official SDK
from backboard import BackboardClient

# Conditional import for transformers to handle environments without it
try:
    from transformers import pipeline
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class TranscriptProcessingService:
    """Service for processing transcripts using Backboard's persistent memory API and local PII models."""
    
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
        
        # PII model attributes
        self._pii_pipeline: Optional[Any] = None
        self._pii_model_loaded = False
        self.pii_model_name = "ab-ai/PII-Model-Phi3-Mini"
        
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
            elif content.startswith("```"):
                content = content.replace("```", "", 1).strip()
            
            return json.loads(content)
                
        except Exception as e:
            # Enhanced error logging
            print(f"Backboard API Error: {str(e)}")
            raise RuntimeError(f"Backboard SDK Error: {str(e)}")

    def _load_pii_model(self):
        """Lazy load the PII detection model using the correct text-generation pipeline."""
        if self._pii_model_loaded:
            return
        
        if not HAS_TRANSFORMERS:
            print("Warning: transformers library not installed. Falling back to regex-based PII detection.")
            self._pii_model_loaded = True
            return
        
        try:
            print(f"Loading PII model: {self.pii_model_name}...")
            
            # Optimization for Apple Silicon (M1/M2/M3) if available, otherwise CUDA or CPU
            device_map = "auto"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            # CORRECTED: Use 'text-generation' pipeline for Causal LM (Phi-3)
            # This fixes the "weights not initialized" error
            self._pii_pipeline = pipeline(
                "text-generation",
                model=self.pii_model_name,
                trust_remote_code=True,
                device_map=device_map,
                torch_dtype=torch_dtype
            )
            
            print("PII model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load PII model: {str(e)}. Falling back to regex-based PII detection.")
            self._pii_pipeline = None
        
        self._pii_model_loaded = True
    
    def _remove_pii_with_model(self, text: str) -> str:
        """Use the PII-Model-Phi3-Mini to detect and redact PII via prompting."""
        self._load_pii_model()
        
        if self._pii_pipeline is None:
            raise Exception("PII model not available")
        
        try:
            # Construct the prompt format expected by Phi-3 Instruct models
            # We explicitly ask it to output the REDACTED text, not just tags.
            prompt = f"""<|system|>
You are a PII (Personally Identifiable Information) redaction assistant. 
Your task is to identify and redact all PII from the user's text.
Replace names, email addresses, phone numbers, addresses, social security numbers, 
and credit card numbers with [REDACTED]. Return ONLY the redacted text.
<|end|>
<|user|>
{text}
<|end|>
<|assistant|>"""
            
            # Generate response
            # max_new_tokens should be roughly length of input + buffer
            input_len = len(text.split())
            max_tokens = min(2048, int(input_len * 1.5) + 100)
            
            result = self._pii_pipeline(
                prompt, 
                max_new_tokens=max_tokens,
                do_sample=False, # Deterministic output is better for redaction
                temperature=0.0
            )
            
            # Extract the generated text after the prompt
            generated_text = result[0]["generated_text"]
            # Phi-3 output usually includes the prompt, so we split by the assistant tag
            if "<|assistant|>" in generated_text:
                redacted_text = generated_text.split("<|assistant|>")[-1].strip()
            else:
                redacted_text = generated_text.replace(prompt, "").strip()
            
            return redacted_text
            
        except Exception as e:
            print(f"Error in model-based PII detection: {str(e)}")
            raise
    
    def _remove_pii_with_regex(self, text: str) -> str:
        """
        Robust pattern-based PII redaction (fallback method).
        Includes comprehensive patterns for financial data.
        """
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        
        # Redact phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        text = re.sub(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        
        # Redact SSN patterns (US)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        
        # Redact credit card numbers (basic pattern)
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CC_REDACTED]', text)
        
        # Redact potential addresses (Street/Ave/etc)
        address_pattern = r'\b\d{1,5}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b'
        text = re.sub(address_pattern, '[ADDRESS_REDACTED]', text, flags=re.IGNORECASE)
        
        return text
    
    def remove_pii(self, text: str) -> str:
        """Remove PII using model-based approach with regex fallback."""
        try:
            # Try model-based PII detection first
            return self._remove_pii_with_model(text)
        except Exception as e:
            print(f"Model-based PII detection failed, switching to regex fallback: {str(e)}")
            # Fallback to regex-based detection
            return self._remove_pii_with_regex(text)

    async def process_transcript(
        self, 
        transcript_text: str,
        base_filename: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Complete async pipeline: PII removal -> Structured output -> Save results.
        """
        # Step 1: Remove PII (Synchronous CPU/GPU operation)
        # Note: In a heavy production app, you might want to run this in a thread pool
        pii_cleaned_text = self.remove_pii(transcript_text)
        
        # Save PII-cleaned text
        pii_cleaned_path = output_dir / f"{base_filename}_pii_cleaned.txt"
        with open(pii_cleaned_path, 'w', encoding='utf-8') as f:
            f.write(pii_cleaned_text)
        
        # Step 2: Generate structured output (awaiting the async IO call)
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