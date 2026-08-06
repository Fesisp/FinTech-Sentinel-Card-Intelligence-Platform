"""
Enterprise Data Contracts and Domain Models (Pydantic v2).
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class CardValidationRequest(BaseModel):
    card_number: str = Field(
        ...,
        description="Raw credit card number (spaces or hyphens allowed)",
        json_schema_extra={"example": "4111 1111 1111 1111"}
    )
    include_risk_analysis: bool = Field(default=True, description="Whether to include advanced fraud risk scoring")


class BINLookupRequest(BaseModel):
    bin_number: str = Field(
        ...,
        description="First 6 to 8 digits of the payment card",
        json_schema_extra={"example": "411111"}
    )


class RiskAssessment(BaseModel):
    score: int = Field(..., description="Fraud risk score from 0 (Safe) to 100 (High Risk)")
    level: str = Field(..., description="Risk Level: LOW, MEDIUM, HIGH, CRITICAL")
    flags: List[str] = Field(..., description="Triggered security anomaly flags")
    entropy: float = Field(..., description="Shannon entropy score of the PAN string")


class CardValidationResponse(BaseModel):
    masked_card: str = Field(..., description="PCI-DSS compliant masked card number (PAN)")
    bin: str = Field(..., description="First 6 digits (BIN/IIN)")
    last_four: str = Field(..., description="Last 4 digits of the card")
    is_valid_luhn: bool = Field(..., description="Checksum validity per Luhn algorithm (Mod 10)")
    brand: str = Field(..., description="Card issuer scheme (Visa, MasterCard, Elo, Amex, etc.)")
    brand_code: str = Field(..., description="Normalized brand code identifier")
    category: str = Field(..., description="Card product category (Credit, Debit, Store Card, etc.)")
    mii_industry: str = Field(..., description="ISO 7812 Major Industry Identifier classification")
    cvv_length: int = Field(..., description="Standard CVV/CVC length for this brand")
    card_token: str = Field(..., description="PCI-DSS HMAC SHA-256 token for secure database indexing")
    risk_assessment: Optional[RiskAssessment] = Field(None, description="Fraud & Anomaly score details")


class BatchValidationRequest(BaseModel):
    cards: List[str] = Field(..., description="List of card numbers to validate in batch", min_length=1, max_length=500)


class BatchValidationResponse(BaseModel):
    total_processed: int = Field(...)
    valid_count: int = Field(...)
    invalid_count: int = Field(...)
    high_risk_count: int = Field(...)
    results: List[CardValidationResponse] = Field(...)


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    pci_dss_compliant: bool
    engine: str
