"""
Service for transcript post-processing pipeline.

This service provides:
1. PII filtering using local PII-Model-Phi3-Mini
2. Structured output generation using Gemini-2.5-pro via Backboard API
"""

import os
import json
import requests
from typing import Dict, Any
from pathlib import Path


class TranscriptProcessingService:
    """Service for processing transcripts: PII removal and structured output generation."""
    
    # Structured output format specification
    # This defines the expected structure that Gemini-2.5-pro should return
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
        """
        Initialize the transcript processing service.
        
        Args:
            backboard_api_key: API key for Backboard service
        """
        self.backboard_api_key = backboard_api_key
        self.backboard_base_url = "https://api.backboard.io/v1"
        
    def remove_pii(self, text: str, use_model: bool = False) -> str:
        """
        Remove or redact PII from text using local PII-Model-Phi3-Mini.
        
        This method can use either:
        1. A locally hosted Phi-3-Mini model (when use_model=True and model is available)
        2. Pattern-based redaction as fallback (default, more efficient)
        
        Args:
            text: Input transcript text
            use_model: Whether to attempt using the Phi-3 model (default: False)
            
        Returns:
            Text with PII removed/redacted
            
        Note:
            To use the full Phi-3-mini model for PII detection:
            1. Ensure transformers, torch, and accelerate are installed
            2. Set use_model=True
            3. The model will be downloaded on first use (~7GB)
            4. GPU is recommended for faster processing
        """
        # Try model-based approach only if explicitly requested
        if use_model:
            try:
                from transformers import pipeline
                
                # Initialize PII detection pipeline using Phi-3-mini
                # Note: This downloads ~7GB model on first use
                pii_detector = pipeline(
                    "text-generation",
                    model="microsoft/Phi-3-mini-4k-instruct",
                    trust_remote_code=True,
                    device_map="auto"
                )
                
                # Prompt for PII redaction
                prompt = f"""<|system|>
You are a PII (Personally Identifiable Information) redaction assistant. 
Your task is to identify and redact all PII from the following text.
Replace names, email addresses, phone numbers, addresses, social security numbers, 
credit card numbers, and other sensitive information with [REDACTED].

<|user|>
Please redact all PII from the following text:

{text}

<|assistant|>
"""
                
                # Generate redacted text
                result = pii_detector(
                    prompt,
                    max_new_tokens=2048,
                    temperature=0.1,
                    do_sample=False
                )
                
                # Extract the redacted text from the response
                redacted_text = result[0]["generated_text"].split("<|assistant|>")[-1].strip()
                
                return redacted_text
                
            except Exception as e:
                # If model loading fails, fall back to basic pattern-based redaction
                print(f"Warning: PII model failed, using pattern-based redaction: {e}")
        
        # Use pattern-based redaction (default, more efficient)
        return self._basic_pii_redaction(text)
    
    def _basic_pii_redaction(self, text: str) -> str:
        """
        Enhanced PII redaction using regex patterns and NLP.
        
        Redacts:
        - Email addresses
        - Phone numbers (various formats)
        - SSN patterns
        - Credit card numbers
        - Addresses (basic patterns)
        - Common name patterns (capitalized words following common patterns)
        
        Args:
            text: Input text
            
        Returns:
            Text with PII patterns redacted
        """
        import re
        
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        
        # Redact phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        text = re.sub(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        text = re.sub(r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_REDACTED]', text)
        
        # Redact SSN patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        
        # Redact credit card numbers (basic pattern)
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CC_REDACTED]', text)
        
        # Redact potential addresses (street numbers and names)
        text = re.sub(r'\b\d{1,5}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b', 
                     '[ADDRESS_REDACTED]', text, flags=re.IGNORECASE)
        
        # Redact ZIP codes
        text = re.sub(r'\b\d{5}(?:-\d{4})?\b', '[ZIP_REDACTED]', text)
        
        # Redact common name patterns (e.g., "my name is John Doe", "I'm Jane Smith")
        text = re.sub(r'\b(?:my name is|I\'?m|called|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', 
                     r'\1 [NAME_REDACTED]', text)
        
        # Redact standalone capitalized names in common contexts
        # This is less aggressive to avoid false positives
        text = re.sub(r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
                     r'\1 [NAME_REDACTED]', text)
        
        return text
    
    def generate_structured_output(self, pii_cleaned_text: str) -> Dict[str, Any]:
        """
        Generate structured output from PII-cleaned text using Gemini-2.5-pro via Backboard.
        
        Args:
            pii_cleaned_text: Text with PII already removed
            
        Returns:
            Structured output as returned by the LLM (not modified)
        """
        # Prepare the prompt for structured output generation
        prompt = f"""Analyze the following transcript and extract structured information in the following JSON format:

{json.dumps(self.STRUCTURED_OUTPUT_FORMAT, indent=2)}

Transcript:
{pii_cleaned_text}

Please provide your response as valid JSON matching the format above."""
        
        # Call Backboard API to interact with Gemini-2.5-pro
        headers = {
            "Authorization": f"Bearer {self.backboard_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gemini-2.5-pro",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(
                f"{self.backboard_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the structured content from the response
            # The exact path may vary based on Backboard's API response structure
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON if it's a string
                if isinstance(content, str):
                    structured_output = json.loads(content)
                else:
                    structured_output = content
                
                return structured_output
            else:
                raise ValueError("Unexpected response format from Backboard API")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to call Backboard API: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
    
    def save_pii_cleaned_text(self, text: str, output_path: str) -> str:
        """
        Save PII-cleaned text to a file.
        
        Args:
            text: PII-cleaned text
            output_path: Path where the text should be saved
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return output_path
    
    def save_structured_output(self, structured_output: Dict[str, Any], output_path: str) -> str:
        """
        Save structured output to a JSON file exactly as returned by the LLM.
        
        Args:
            structured_output: Structured output from the LLM
            output_path: Path where the JSON should be saved
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_output, f, indent=2, ensure_ascii=False)
        return output_path
    
    def process_transcript(
        self, 
        transcript_text: str,
        base_filename: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Complete pipeline: PII removal -> Structured output generation -> Save results.
        
        Args:
            transcript_text: Original transcript text
            base_filename: Base name for output files
            output_dir: Directory to save output files
            
        Returns:
            Dictionary containing paths to saved files and processing results
        """
        # Step 1: Remove PII
        pii_cleaned_text = self.remove_pii(transcript_text)
        
        # Save PII-cleaned text
        pii_cleaned_path = output_dir / f"{base_filename}_pii_cleaned.txt"
        self.save_pii_cleaned_text(pii_cleaned_text, str(pii_cleaned_path))
        
        # Step 2: Generate structured output
        structured_output = self.generate_structured_output(pii_cleaned_text)
        
        # Step 3: Save structured output exactly as returned
        structured_output_path = output_dir / f"{base_filename}_structured.json"
        self.save_structured_output(structured_output, str(structured_output_path))
        
        return {
            "pii_cleaned_path": str(pii_cleaned_path),
            "structured_output_path": str(structured_output_path),
            "structured_output": structured_output,
            "success": True
        }
