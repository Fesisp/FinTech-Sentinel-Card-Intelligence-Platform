"""
Enterprise Payment Card Brand Specification and Intelligent BIN Matching Engine.
Supports ISO/IEC 7812 MII classifications, global and domestic card schemes.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from app.core.luhn import clean_card_number


@dataclass
class BrandSpec:
    name: str
    code: str
    valid_lengths: List[int]
    cvv_length: int
    category: str  # Commercial Bank, Credit, Debit, Prepaid
    mii_industry: str  # Major Industry Identifier description


MAJOR_INDUSTRY_IDENTIFIERS = {
    "1": "Airlines",
    "2": "Airlines / Financial & Future Industry",
    "3": "Travel & Entertainment (Amex, Diners)",
    "4": "Banking & Financial (Visa)",
    "5": "Banking & Financial (Mastercard)",
    "6": "Merchandising & Banking (Discover, Regional)",
    "7": "Petroleum & Industry",
    "8": "Healthcare & Telecommunications",
    "9": "National Assignment",
}


def get_mii_description(digit: str) -> str:
    """Returns ISO/IEC 7812 Major Industry Identifier classification."""
    return MAJOR_INDUSTRY_IDENTIFIERS.get(digit, "Unknown Industry")


def detect_card_brand(number: str) -> Optional[BrandSpec]:
    """
    Detects the card brand and metadata specification for a given card number.
    """
    n = clean_card_number(number)
    ln = len(n)
    if not n:
        return None

    first_digit = n[0]
    mii_desc = get_mii_description(first_digit)

    # Elo (Brazilian local scheme - highest priority check due to overlapping BINs)
    elo_prefixes_6 = ("506699", "509000", "650031", "650032", "650033", "650051")
    elo_prefixes_4 = ("4011", "4312", "4389", "4514", "4576", "5041", "5067", "5090", "6277", "6362", "6363", "6500", "6504", "6505", "6516", "6550")
    if (len(n) >= 6 and n.startswith(elo_prefixes_6)) or (len(n) >= 4 and n.startswith(elo_prefixes_4)):
        return BrandSpec("Elo", "ELO", [16], 3, "Credit / Debit / Regional", mii_desc)

    # Hipercard (Brazilian scheme)
    if len(n) >= 6 and n.startswith(("606282", "384100", "384140", "384160", "637095", "637568", "637599")):
        return BrandSpec("Hipercard", "HIPERCARD", [13, 16, 19], 3, "Credit / Store Card", mii_desc)
    if ln >= 13 and (n.startswith("3841") or n.startswith("6062")):
        return BrandSpec("Hipercard", "HIPERCARD", [13, 16, 19], 3, "Credit / Store Card", mii_desc)

    # Visa
    if n.startswith("4") and ln in (13, 16, 19):
        return BrandSpec("Visa", "VISA", [13, 16, 19], 3, "Credit / Debit", mii_desc)

    # Mastercard
    if ln == 16:
        try:
            p2 = int(n[:2])
            p4 = int(n[:4])
            if (51 <= p2 <= 55) or (2221 <= p4 <= 2720):
                return BrandSpec("MasterCard", "MASTERCARD", [16], 3, "Credit / Debit", mii_desc)
        except ValueError:
            pass

    # American Express
    if ln == 15 and n.startswith(("34", "37")):
        return BrandSpec("American Express", "AMEX", [15], 4, "Credit / Charge", mii_desc)

    # Discover
    if ln in (16, 19):
        if n.startswith("6011") or n.startswith("65") or (len(n) >= 3 and 644 <= int(n[:3]) <= 649):
            return BrandSpec("Discover", "DISCOVER", [16, 19], 3, "Credit", mii_desc)
        if len(n) >= 6 and 622126 <= int(n[:6]) <= 622925:
            return BrandSpec("Discover", "DISCOVER", [16, 19], 3, "Credit", mii_desc)

    # JCB
    if 16 <= ln <= 19 and len(n) >= 4 and 3528 <= int(n[:4]) <= 3589:
        return BrandSpec("JCB", "JCB", [16, 17, 18, 19], 3, "Credit", mii_desc)

    # Diners Club
    if 14 <= ln <= 19 and (n.startswith("36") or n.startswith("38") or (len(n) >= 3 and 300 <= int(n[:3]) <= 305)):
        return BrandSpec("Diners Club", "DINERS", [14, 15, 16, 17, 18, 19], 3, "Credit / Travel", mii_desc)

    # UnionPay
    if 16 <= ln <= 19 and n.startswith(("62", "81")):
        return BrandSpec("UnionPay", "UNIONPAY", [16, 17, 18, 19], 3, "Credit / Debit", mii_desc)

    # Maestro
    if 12 <= ln <= 19 and n.startswith(("5018", "5020", "5038", "5893", "6304", "6759", "6761", "6762", "6763")):
        return BrandSpec("Maestro", "MAESTRO", list(range(12, 20)), 3, "Debit", mii_desc)

    # Mir
    if ln == 16 and len(n) >= 4 and 2200 <= int(n[:4]) <= 2204:
        return BrandSpec("Mir", "MIR", [16], 3, "National Payment Scheme", mii_desc)

    # Aura
    if 16 <= ln <= 19 and n.startswith("5078"):
        return BrandSpec("Aura", "AURA", [16, 19], 3, "Credit Card", mii_desc)

    # Cabal
    if ln == 16 and n.startswith(("6042", "6043")):
        return BrandSpec("Cabal", "CABAL", [16], 3, "Credit Card", mii_desc)

    return None
