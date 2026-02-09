#!/usr/bin/env python3
"""
Unit tests for PII redaction functionality.
"""

import sys
sys.path.insert(0, '.')

from filtertext.service import TranscriptProcessingService

def test_pii_redaction():
    """Test PII redaction with various patterns."""
    
    # Initialize service (API key not needed for PII testing)
    service = TranscriptProcessingService(backboard_api_key="test_key")
    
    # Test text with various PII types
    test_text = """
    Hello, my name is John Doe and I work at Example Corp.
    You can reach me at john.doe@example.com or call me at 555-123-4567.
    My alternative number is (555) 987-6543.
    I live at 123 Main Street, Springfield, 12345.
    My SSN is 123-45-6789 and my credit card is 1234 5678 9012 3456.
    Dr. Jane Smith from ABC Corporation will be joining us.
    The meeting is scheduled for next Tuesday at 3pm.
    """
    
    print("=" * 70)
    print("PII Redaction Test")
    print("=" * 70)
    
    print("\nOriginal text:")
    print(test_text)
    
    print("\n" + "-" * 70)
    print("After PII redaction:")
    print("-" * 70)
    
    redacted_text = service.remove_pii(test_text, use_model=False)
    print(redacted_text)
    
    print("\n" + "=" * 70)
    print("PII Patterns Found and Redacted:")
    print("=" * 70)
    
    # Check what was redacted
    patterns = {
        "Email": "[EMAIL_REDACTED]" in redacted_text,
        "Phone": "[PHONE_REDACTED]" in redacted_text,
        "SSN": "[SSN_REDACTED]" in redacted_text,
        "Credit Card": "[CC_REDACTED]" in redacted_text,
        "Address": "[ADDRESS_REDACTED]" in redacted_text,
        "ZIP": "[ZIP_REDACTED]" in redacted_text,
    }
    
    for pattern, found in patterns.items():
        status = "✓ Redacted" if found else "✗ Not found"
        print(f"{pattern:.<30} {status}")
    
    print("=" * 70)
    
    # Return success if key patterns were redacted
    success = all([
        patterns["Email"],
        patterns["Phone"],
        patterns["SSN"],
        patterns["Credit Card"],
        patterns["Address"]
    ])
    
    if success:
        print("\n✓ All critical PII patterns successfully redacted!")
    else:
        print("\n✗ Some PII patterns were not redacted.")
    
    return success

if __name__ == "__main__":
    success = test_pii_redaction()
    exit(0 if success else 1)
