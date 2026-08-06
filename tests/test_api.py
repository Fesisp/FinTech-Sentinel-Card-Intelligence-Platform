from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert data["pci_dss_compliant"] is True


def test_single_card_validation_api():
    payload = {
        "card_number": "4111 1111 1111 1111",
        "include_risk_analysis": True
    }
    res = client.post("/api/v1/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["brand"] == "Visa"
    assert data["is_valid_luhn"] is True
    assert "risk_assessment" in data


def test_batch_card_validation_api():
    payload = {
        "cards": ["4111111111111111", "5555555555554444", "4111111111111112"]
    }
    res = client.post("/api/v1/validate/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 3
    assert len(data["results"]) == 3


def test_bin_lookup_api():
    res = client.get("/api/v1/bin/411111")
    assert res.status_code == 200
    data = res.json()
    assert data["brand"] == "Visa"
    assert "Banking & Financial" in data["mii_industry"]
