from app.core.security import mask_card_number, generate_card_token, evaluate_fraud_risk, calculate_entropy


def test_pci_card_masking():
    masked = mask_card_number("4111111111111111")
    assert masked.startswith("4111 11")
    assert masked.endswith("1111")
    assert "****" in masked


def test_hmac_token_generation():
    token1 = generate_card_token("4111111111111111")
    token2 = generate_card_token("4111111111111111")
    assert token1.startswith("TOK_")
    assert token1 == token2  # Deterministic HMAC with secret key


def test_entropy_calculation():
    e_mono = calculate_entropy("1111111111111111")
    e_varied = calculate_entropy("1234567890987654")
    assert e_mono == 0.0
    assert e_varied > e_mono


def test_fraud_risk_assessment_known_test_card():
    risk = evaluate_fraud_risk("4111111111111111", is_luhn_valid=True, brand="Visa")
    assert risk["score"] > 0
    assert any("KNOWN_TEST_PAN" in flag for flag in risk["flags"])


def test_fraud_risk_assessment_mono_digit():
    risk = evaluate_fraud_risk("9999999999999999", is_luhn_valid=False, brand=None)
    assert risk["level"] in ("HIGH", "CRITICAL")
