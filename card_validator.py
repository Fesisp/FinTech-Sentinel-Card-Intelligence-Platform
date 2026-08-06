"""Credit Card Brand Identifier & Validation Engine (Enterprise Bridge).

This module provides CLI and import compatibility for legacy scripts while leveraging
the enterprise FinTech Sentinel engine underneath.

Usage:
  python card_validator.py 4111111111111111 378282246310005
  python card_validator.py --server  # Starts the FastAPI Banking Server & Dashboard
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Tuple

from app.core.luhn import clean_card_number as _clean, validate_luhn as luhn_check
from app.core.brands import detect_card_brand
from app.services.validator_service import CardValidatorService


def detect_brand(number: str) -> Optional[str]:
    """Detects card brand name from card number."""
    spec = detect_card_brand(number)
    return spec.name if spec else None


def format_result(number: str) -> Tuple[str, str, bool]:
    """Returns (clean_number, brand_or_msg, luhn_ok)."""
    clean = _clean(number)
    brand = detect_brand(clean) or "Unknown Brand"
    luhn_ok = luhn_check(clean)
    return clean, brand, luhn_ok


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="FinTech Sentinel - Credit Card Validation Engine")
    p.add_argument("numbers", nargs="*", help="Card numbers to analyze. If empty, enters interactive prompt.")
    p.add_argument("--server", action="store_true", help="Launch enterprise web dashboard and API server.")
    p.add_argument("--port", type=int, default=8000, help="Port for API server (default: 8000)")
    return p.parse_args()


def main():
    args = _parse_args()

    if args.server:
        import uvicorn
        print(f"🚀 Launching FinTech Sentinel Enterprise Web Dashboard at http://localhost:{args.port} ...")
        uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=False)
        return

    if not args.numbers:
        # Interactive Mode
        print("--- FinTech Sentinel Credit Card Validator ---")
        print("Press Enter on empty line to exit.")
        while True:
            try:
                s = input("Card number: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not s:
                break
            res = CardValidatorService.validate_card(s)
            luhn_str = "valid" if res.is_valid_luhn else "invalid"
            print(f"{res.masked_card} -> {res.brand} | Luhn: {luhn_str} | Risk: {res.risk_assessment.level if res.risk_assessment else 'N/A'}")
    else:
        for s in args.numbers:
            res = CardValidatorService.validate_card(s)
            luhn_str = "valid" if res.is_valid_luhn else "invalid"
            print(f"{res.masked_card} -> {res.brand} | Luhn: {luhn_str} | Risk: {res.risk_assessment.level if res.risk_assessment else 'N/A'}")


if __name__ == "__main__":
    main()