"""
Security, Masking, PCI-DSS Compliance, and Fraud Risk Detection Engine.
"""
from __future__ import annotations

import hmac
import hashlib
import math
from typing import Dict, Any, List
from app.core.config import settings
from app.core.luhn import clean_card_number


def mask_card_number(number: str, head: int = settings.UNMASKED_HEAD_DIGITS, tail: int = settings.UNMASKED_TAIL_DIGITS) -> str:
    """
    PCI-DSS Compliant Card Masking.
    Keeps first 6 (BIN) and last 4 digits visible; replaces middle digits with '*'.
    Format is formatted with 4-digit grouping for legibility.
    """
    clean = clean_card_number(number)
    length = len(clean)
    if length < 10:
        # For short test numbers or non-standard lengths
        if length <= 4:
            return "*" * length
        return clean[:2] + "*" * (length - 4) + clean[-2:]

    masked_body = settings.PCI_MASK_CHAR * (length - head - tail)
    full_masked = clean[:head] + masked_body + clean[-tail:]

    # Format in groups of 4 for presentation
    grouped = [full_masked[i:i+4] for i in range(0, len(full_masked), 4)]
    return " ".join(grouped)


def generate_card_token(number: str, secret_key: str = settings.TOKEN_SECRET_KEY) -> str:
    """
    Generates a secure HMAC-SHA256 non-reversible token representing the card number.
    Allows searching and correlation in logs/databases without storing the raw PAN.
    """
    clean = clean_card_number(number)
    if not clean:
        return ""
    token_bytes = hmac.new(
        secret_key.encode("utf-8"),
        clean.encode("utf-8"),
        hashlib.sha256
    ).digest()
    return "TOK_" + token_bytes.hex()[:24].upper()


def calculate_entropy(s: str) -> float:
    """Calculates Shannon entropy of a string of digits."""
    if not s:
        return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def evaluate_fraud_risk(number: str, is_luhn_valid: bool, brand: str | None) -> Dict[str, Any]:
    """
    Analyzes card patterns for fraud risk indicators.
    Returns risk score (0-100), risk level (LOW, MEDIUM, HIGH, CRITICAL), and triggered rules.
    """
    clean = clean_card_number(number)
    risk_score = 0
    flags: List[str] = []

    if not clean:
        return {
            "score": 100,
            "level": "CRITICAL",
            "flags": ["EMPTY_CARD_NUMBER"],
            "entropy": 0.0
        }

    # Rule 1: Failed Luhn Checksum
    if not is_luhn_valid:
        risk_score += 40
        flags.append("FAILED_LUHN_CHECKSUM")

    # Rule 2: Unknown Brand or Unrecognized BIN
    if not brand or brand == "Unknown Brand":
        risk_score += 25
        flags.append("UNRECOGNIZED_ISSUER_BIN")

    # Rule 3: Known Test / Dummy Card Numbers
    KNOWN_TEST_CARDS = {
        "4111111111111111": "Visa Test Card",
        "4242424242424242": "Stripe/Adyen Test Card",
        "5555555555554444": "Mastercard Test Card",
        "378282246310005": "Amex Test Card",
        "4000000000000002": "Visa Refused Test Card",
    }
    if clean in KNOWN_TEST_CARDS:
        risk_score += 35
        flags.append(f"KNOWN_TEST_PAN ({KNOWN_TEST_CARDS[clean]})")

    # Rule 4: High Repetitive Digits (Low Entropy)
    entropy = calculate_entropy(clean)
    if entropy < 1.8 and len(clean) >= 13:
        risk_score += 30
        flags.append(f"SUSPICIOUS_LOW_ENTROPY ({entropy:.2f})")

    # Rule 5: Monotonic Sequential Digits (e.g., 123456789 or 987654321)
    if "123456" in clean or "654321" in clean or "012345" in clean:
        risk_score += 35
        flags.append("SEQUENTIAL_DIGIT_PATTERN")

    # Rule 6: Identical repeated digit strings (e.g. 8888888888)
    if len(set(clean)) <= 2:
        risk_score += 40
        flags.append("MONO_DIGIT_PATTERN")

    # Determine risk level
    if risk_score == 0:
        level = "LOW"
    elif risk_score < 30:
        level = "LOW"
    elif risk_score < 60:
        level = "MEDIUM"
    elif risk_score < 85:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return {
        "score": min(risk_score, 100),
        "level": level,
        "flags": flags if flags else ["NO_RISK_DETECTED"],
        "entropy": round(entropy, 3)
    }
