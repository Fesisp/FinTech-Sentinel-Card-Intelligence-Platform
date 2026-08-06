"""
Luhn Algorithm Checksum Implementation.
PCI-DSS Compliant zero-allocation calculation where applicable.
"""
from __future__ import annotations
import re

_NON_DIGIT_REGEX = re.compile(r"\D")

def clean_card_number(number: str | None) -> str:
    """Removes non-digit characters from the input string."""
    if not number:
        return ""
    return _NON_DIGIT_REGEX.sub("", number)

def validate_luhn(number: str) -> bool:
    """
    Validates a card number using the Luhn checksum algorithm (Mod 10).
    
    Returns:
        bool: True if the card passes the Luhn check, False otherwise.
    """
    cleaned = clean_card_number(number)
    length = len(cleaned)
    
    # Standard card numbers must be between 8 and 19 digits per ISO/IEC 7812
    if length < 8 or length > 19:
        return False

    total = 0
    parity = length % 2
    
    for i, char in enumerate(cleaned):
        digit = ord(char) - 48  # Fast ASCII to integer conversion ('0' = 48)
        if digit < 0 or digit > 9:
            return False
            
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit

    return total % 10 == 0
