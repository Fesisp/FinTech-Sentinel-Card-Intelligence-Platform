import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import card_validator as mod


def test_luhn_valid_examples():
    assert mod.luhn_check("4111111111111111") is True
    assert mod.luhn_check("378282246310005") is True


def test_luhn_invalid_examples():
    assert mod.luhn_check("") is False
    assert mod.luhn_check("4111111111111112") is False


def test_detect_brand_known():
    assert mod.detect_brand("4111111111111111") == "Visa"
    assert mod.detect_brand("5555555555554444") == "MasterCard"
    assert mod.detect_brand("378282246310005") == "American Express"


def test_detect_brand_unknown():
    assert mod.detect_brand("0000000000000000") is None


def test_format_result():
    clean, brand, ok = mod.format_result("4111 1111 1111 1111")
    assert clean == "4111111111111111"
    assert brand == "Visa"
    assert ok is True
