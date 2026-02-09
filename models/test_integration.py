#!/usr/bin/env python3
"""
Integration test for the complete filtertext pipeline with mocked Backboard API.
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, '.')

def test_pipeline_with_mock():
    """Test the complete pipeline with mocked Backboard API."""
    
    from filtertext.service import TranscriptProcessingService
    from pathlib import Path
    
    print("=" * 70)
    print("Integration Test: Complete Pipeline with Mocked Backboard API")
    print("=" * 70)
    
    # Sample transcript text
    sample_text = """
    Hello, my name is John Doe and my email is john.doe@example.com.
    I can be reached at 555-123-4567. My address is 123 Main Street.
    
    We discussed the following topics during our financial advisory session:
    
    1. Portfolio Review: Current allocation is 60% stocks, 30% bonds, 10% cash.
       Total portfolio value is approximately $500,000.
    
    2. Risk Assessment: Client has moderate risk tolerance. Age 45, planning
       retirement at 65. Time horizon is 20 years.
    
    3. Tax Planning: Discussed Roth IRA conversion opportunities and 
       tax-loss harvesting strategies for 2024.
    
    4. Action Items:
       - Rebalance portfolio by end of Q1
       - Schedule follow-up meeting in 3 months
       - Review beneficiary designations
       - Set up automatic contributions of $1,000/month
    
    5. Compliance: All recommendations documented in accordance with 
       fiduciary standards. Client acknowledged understanding of risks.
    """
    
    # Mock Backboard API response
    mock_structured_output = {
        "summary": "Financial advisory session discussing portfolio review, risk assessment, tax planning, and establishing action items for a 45-year-old client with $500K portfolio planning for retirement at 65.",
        "key_points": [
            "Current portfolio allocation: 60% stocks, 30% bonds, 10% cash",
            "Portfolio value: $500,000",
            "Client age: 45, retirement target: 65 (20-year horizon)",
            "Moderate risk tolerance",
            "Tax planning discussed including Roth IRA conversion",
            "Rebalancing needed by end of Q1"
        ],
        "entities": {
            "people": ["[NAME_REDACTED]"],
            "organizations": [],
            "dates": ["Q1", "3 months", "2024"],
            "amounts": ["$500,000", "$1,000/month", "60%", "30%", "10%"]
        },
        "sentiment": "neutral",
        "action_items": [
            "Rebalance portfolio by end of Q1",
            "Schedule follow-up meeting in 3 months",
            "Review beneficiary designations",
            "Set up automatic contributions of $1,000/month"
        ],
        "topics": [
            "Portfolio Review",
            "Risk Assessment",
            "Tax Planning",
            "Retirement Planning",
            "Compliance"
        ]
    }
    
    # Initialize service
    service = TranscriptProcessingService(backboard_api_key="test_key")
    
    print("\n1. Original Transcript:")
    print("-" * 70)
    print(sample_text[:200] + "...")
    
    # Step 1: Test PII removal
    print("\n2. PII Removal:")
    print("-" * 70)
    pii_cleaned = service.remove_pii(sample_text, use_model=False)
    print(pii_cleaned[:300] + "...")
    
    # Verify PII was removed
    assert "[EMAIL_REDACTED]" in pii_cleaned, "Email should be redacted"
    assert "[PHONE_REDACTED]" in pii_cleaned, "Phone should be redacted"
    assert "[ADDRESS_REDACTED]" in pii_cleaned, "Address should be redacted"
    print("✓ PII successfully redacted")
    
    # Step 2: Test structured output generation with mocked API
    print("\n3. Structured Output Generation (Mocked):")
    print("-" * 70)
    
    # Mock the requests.post call
    with patch('requests.post') as mock_post:
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(mock_structured_output)
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the method
        structured_output = service.generate_structured_output(pii_cleaned)
        
        # Verify the result
        print(json.dumps(structured_output, indent=2))
        
        assert "summary" in structured_output, "Should have summary"
        assert "key_points" in structured_output, "Should have key_points"
        assert "action_items" in structured_output, "Should have action_items"
        print("\n✓ Structured output generated successfully")
    
    # Step 3: Test saving outputs
    print("\n4. Saving Outputs:")
    print("-" * 70)
    
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save PII-cleaned text
    pii_path = service.save_pii_cleaned_text(
        pii_cleaned, 
        str(output_dir / "test_pii_cleaned.txt")
    )
    print(f"✓ PII-cleaned text saved to: {pii_path}")
    
    # Save structured output
    structured_path = service.save_structured_output(
        mock_structured_output,
        str(output_dir / "test_structured.json")
    )
    print(f"✓ Structured output saved to: {structured_path}")
    
    # Verify files exist
    assert os.path.exists(pii_path), "PII-cleaned file should exist"
    assert os.path.exists(structured_path), "Structured output file should exist"
    
    # Read back and verify
    with open(structured_path, 'r') as f:
        saved_data = json.load(f)
        assert saved_data == mock_structured_output, "Saved data should match original"
    
    print("\n5. Complete Pipeline Test:")
    print("-" * 70)
    
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(mock_structured_output)}}]
        }
        mock_post.return_value = mock_response
        
        # Run complete pipeline
        result = service.process_transcript(
            transcript_text=sample_text,
            base_filename="integration_test",
            output_dir=output_dir
        )
        
        print(f"✓ PII-cleaned file: {result['pii_cleaned_path']}")
        print(f"✓ Structured output file: {result['structured_output_path']}")
        print(f"✓ Pipeline success: {result['success']}")
        
        assert result['success'], "Pipeline should complete successfully"
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED!")
    print("=" * 70)
    
    # Cleanup
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    return True

if __name__ == "__main__":
    try:
        success = test_pipeline_with_mock()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
