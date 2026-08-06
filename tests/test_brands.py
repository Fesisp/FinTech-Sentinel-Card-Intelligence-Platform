from app.core.brands import detect_card_brand, get_mii_description


def test_brand_detection_visa():
    spec = detect_card_brand("4000000000000")
    assert spec is not None
    assert spec.name == "Visa"
    assert spec.code == "VISA"


def test_brand_detection_mastercard():
    spec = detect_card_brand("5100000000000000")
    assert spec is not None
    assert spec.name == "MasterCard"

    spec2 = detect_card_brand("2221000000000000")
    assert spec2 is not None
    assert spec2.name == "MasterCard"


def test_brand_detection_elo():
    spec = detect_card_brand("6363680000000000")
    assert spec is not None
    assert spec.name == "Elo"
    assert spec.code == "ELO"


def test_brand_detection_amex():
    spec = detect_card_brand("340000000000000")
    assert spec is not None
    assert spec.name == "American Express"


def test_brand_detection_discover():
    spec = detect_card_brand("6011000000000000")
    assert spec is not None
    assert spec.name == "Discover"


def test_mii_description():
    assert get_mii_description("4") == "Banking & Financial (Visa)"
    assert get_mii_description("5") == "Banking & Financial (Mastercard)"
    assert get_mii_description("3") == "Travel & Entertainment (Amex, Diners)"
