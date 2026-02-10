import os
import json
import asyncio
import re
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from backboard import BackboardClient

# Conditional import for transformers
try:
    from transformers import pipeline
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class TranscriptProcessingService:
    """
    Service for processing transcripts using Backboard's persistent memory API 
    and a hybrid PII detection system (NER Model + Advanced Regex).
    """
    
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
        self.client = BackboardClient(api_key=backboard_api_key)
        self.provider = "google"
        self.model = "gemini-2.5-pro"
        
        # PII Model: "obi/deid_roberta_i2b2"
        # A 480MB BERT model fine-tuned on the i2b2 dataset (Gold standard for de-identification)
        self.pii_model_name = "obi/deid_roberta_i2b2"
        self._pii_pipeline: Optional[Any] = None
        self._pii_model_loaded = False
        
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
            # 1. Create an assistant 
            assistant = await self.client.create_assistant(
                name="Transcript Analyzer",
                system_prompt="You are an expert financial transcript analyst. Always return valid JSON."
            )
            
            # 2. Create a thread
            thread = await self.client.create_thread(assistant.assistant_id)
            
            # 3. Send message
            response = await self.client.add_message(
                thread_id=thread.thread_id,
                content=prompt,
                llm_provider=self.provider,
                model_name=self.model,
                stream=False
            )
            
            content = response.content
            
            # Clean potential markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.replace("```", "").strip()
            
            return json.loads(content)
                
        except Exception as e:
            raise RuntimeError(f"Backboard SDK Error: {str(e)}")

    def _load_pii_model(self):
        """Lazy load the lightweight NER model."""
        if self._pii_model_loaded:
            return
        
        if not HAS_TRANSFORMERS:
            print("Warning: transformers library not installed. Using Regex only.")
            self._pii_model_loaded = True
            return
        
        try:
            print(f"Loading PII model: {self.pii_model_name}...")
            # We use 'aggregation_strategy="simple"' to auto-merge "Sam" + "##arth" -> "Samarth"
            # device=-1 forces CPU (More stable for small models on Mac Air than MPS)
            self._pii_pipeline = pipeline(
                "token-classification",
                model=self.pii_model_name,
                aggregation_strategy="simple", 
                device=-1 
            )
            print("PII model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load PII model: {str(e)}. Falling back to regex.")
        
        self._pii_model_loaded = True
    
    def _remove_pii_with_regex(self, text: str) -> str:
        """
        Advanced Regex Redaction for cases the model might miss.
        Includes patterns for: Credit Cards, SSNs, IPs, IBANs, Emails, Phones.
        """
        # 1. Credit Card Numbers (Visa, MasterCard, Amex, Discover)
        # Matches 13-19 digits with optional dashes/spaces
        cc_pattern = r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b'
        text = re.sub(cc_pattern, '[CREDIT_CARD_REDACTED]', text)
        
        # 2. International Bank Account Numbers (IBAN) - Generic format
        iban_pattern = r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b'
        text = re.sub(iban_pattern, '[IBAN_REDACTED]', text)
        
        # 3. Emails (Case insensitive)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = re.sub(email_pattern, '[EMAIL_REDACTED]', text, flags=re.IGNORECASE)
        
        # 4. US Social Security Numbers (SSN)
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        text = re.sub(ssn_pattern, '[SSN_REDACTED]', text)
        
        # 5. IPv4 Addresses
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        text = re.sub(ip_pattern, '[IP_REDACTED]', text)
        
        # 6. Phone Numbers (US & International formats)
        # Matches: +1-555-555-5555, (555) 555-5555, 555.555.5555
        phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        text = re.sub(phone_pattern, '[PHONE_REDACTED]', text)

        return text

    def remove_pii(self, text: str) -> str:
        """
        Hybrid PII Removal:
        1. Runs Regex first (fastest, catches clear patterns like CC numbers).
        2. Runs NER Model second (catches context-dependent names/orgs).
        """
        # Step 1: Regex Redaction
        text = self._remove_pii_with_regex(text)
        
        # Step 2: Model Redaction (NER)
        try:
            self._load_pii_model()
            
            if self._pii_pipeline:
                # The pipeline returns a list of entities: [{'entity_group': 'PER', 'score': 0.99, 'word': 'Samarth', 'start': 0, 'end': 7}, ...]
                entities = self._pii_pipeline(text)
                
                # We must replace from END to START to keep indices valid
                # Sort entities by start index descending
                entities = sorted(entities, key=lambda x: x['start'], reverse=True)
                
                # Convert string to list of characters for mutable replacement
                text_chars = list(text)
                
                for entity in entities:
                    start = entity['start']
                    end = entity['end']
                    label = entity['entity_group'] # e.g., PER, LOC, ORG, DATE
                    
                    # Create redaction tag
                    replacement = f"[{label}_REDACTED]"
                    
                    # Replace the slice
                    text_chars[start:end] = list(replacement)
                
                text = "".join(text_chars)
                
        except Exception as e:
            print(f"Model PII detection failed (using regex-only result): {str(e)}")
            
        return text

    async def process_transcript(
        self, 
        transcript_text: str,
        base_filename: str,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Complete async pipeline."""
        
        # Step 1: Remove PII (Sync CPU task)
        pii_cleaned_text = self.remove_pii(transcript_text)
        
        # Save PII-cleaned text
        pii_cleaned_path = output_dir / f"{base_filename}_pii_cleaned.txt"
        with open(pii_cleaned_path, 'w', encoding='utf-8') as f:
            f.write(pii_cleaned_text)
        
        # Step 2: Generate structured output (Async I/O task)
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