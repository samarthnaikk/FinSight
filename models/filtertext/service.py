import os
import json
import asyncio
import re
from typing import Dict, Any, Optional
from pathlib import Path
# Import the official SDK
from backboard import BackboardClient

try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

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
        
        # PII model attributes (lazy loading)
        self._pii_tokenizer: Optional[Any] = None
        self._pii_model: Optional[Any] = None
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
            
            return json.loads(content)
                
        except Exception as e:
            raise RuntimeError(f"Backboard SDK Error: {str(e)}")

    def _load_pii_model(self):
        """Lazy load the PII detection model."""
        if self._pii_model_loaded:
            return
        
        if not HAS_TRANSFORMERS:
            print("Warning: transformers library not installed. Falling back to regex-based PII detection.")
            self._pii_model_loaded = True
            return
        
        try:
            print(f"Loading PII model: {self.pii_model_name}...")
            self._pii_tokenizer = AutoTokenizer.from_pretrained(self.pii_model_name)
            self._pii_model = AutoModelForTokenClassification.from_pretrained(self.pii_model_name)
            self._pii_model.eval()
            print("PII model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load PII model: {str(e)}. Falling back to regex-based PII detection.")
        
        self._pii_model_loaded = True
    
    def _remove_pii_with_model(self, text: str) -> str:
        """Use the PII-Model-Phi3-Mini to detect and redact PII."""
        self._load_pii_model()
        
        if self._pii_model is None or self._pii_tokenizer is None:
            # Model didn't load, return text unchanged to trigger fallback
            raise Exception("PII model not available")
        
        try:
            # Tokenize the input text
            inputs = self._pii_tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
            
            # Get predictions
            with torch.no_grad():
                outputs = self._pii_model(**inputs)
            
            # Get predicted labels
            predictions = torch.argmax(outputs.logits, dim=2)
            tokens = self._pii_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            labels = [self._pii_model.config.id2label[pred.item()] for pred in predictions[0]]
            
            # Reconstruct text with PII redacted
            redacted_tokens = []
            current_entity_type = None
            
            for token, label in zip(tokens, labels):
                # Skip special tokens
                if token in [self._pii_tokenizer.cls_token, self._pii_tokenizer.sep_token, 
                            self._pii_tokenizer.pad_token, self._pii_tokenizer.unk_token]:
                    continue
                
                # Check if token is a PII entity (B- or I- prefix indicates entity)
                if label.startswith('B-') or label.startswith('I-'):
                    entity_type = label.split('-')[1]
                    if current_entity_type != entity_type:
                        redacted_tokens.append(f'[{entity_type}_REDACTED]')
                        current_entity_type = entity_type
                else:
                    current_entity_type = None
                    # Clean up subword tokens (remove ## prefix from BERT-style tokenizers)
                    clean_token = token.replace('##', '')
                    redacted_tokens.append(clean_token)
            
            # Join tokens back into text
            redacted_text = ' '.join(redacted_tokens)
            # Clean up extra spaces
            redacted_text = re.sub(r'\s+', ' ', redacted_text).strip()
            
            return redacted_text
            
        except Exception as e:
            print(f"Error in model-based PII detection: {str(e)}")
            raise
    
    def _remove_pii_with_regex(self, text: str) -> str:
        """Pattern-based PII redaction (fallback method)."""
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        return text
    
    def remove_pii(self, text: str) -> str:
        """Remove PII using model-based approach with regex fallback."""
        try:
            # Try model-based PII detection first
            return self._remove_pii_with_model(text)
        except Exception as e:
            print(f"Model-based PII detection failed, using regex fallback: {str(e)}")
            # Fallback to regex-based detection
            return self._remove_pii_with_regex(text)

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