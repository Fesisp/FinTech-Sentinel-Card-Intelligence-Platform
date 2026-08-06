"""
REST API Routes for FinTech Sentinel Card Intelligence Platform.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, status
from app.domain.models import (
    CardValidationRequest,
    CardValidationResponse,
    BatchValidationRequest,
    BatchValidationResponse,
    SystemHealthResponse
)
from app.services.validator_service import CardValidatorService
from app.core.brands import detect_card_brand, get_mii_description
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="System Health & PCI Compliance Status",
    tags=["System Telemetry"]
)
def get_system_health():
    return SystemHealthResponse(
        status="OPERATIONAL",
        version=settings.VERSION,
        pci_dss_compliant=True,
        engine="FinTech Sentinel v2.0 Enterprise Engine"
    )


@router.post(
    "/validate",
    response_model=CardValidationResponse,
    summary="Validate Single Card Number",
    description="Validates card checksum (Luhn), identifies BIN scheme, redacts PAN per PCI-DSS, and assesses fraud risk.",
    tags=["Card Validation"]
)
def validate_single_card(payload: CardValidationRequest):
    if not payload.card_number or not payload.card_number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card number cannot be empty."
        )
    return CardValidatorService.validate_card(payload.card_number, payload.include_risk_analysis)


@router.post(
    "/validate/batch",
    response_model=BatchValidationResponse,
    summary="Batch Card Validation",
    description="High-throughput batch validation for payment gateways and audit logs (Up to 500 cards per request).",
    tags=["Card Validation"]
)
def validate_card_batch(payload: BatchValidationRequest):
    if not payload.cards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch list cannot be empty."
        )
    return CardValidatorService.validate_batch(payload.cards)


@router.get(
    "/bin/{bin_number}",
    summary="BIN Identification & Scheme Lookup",
    description="Inspects BIN/IIN prefix to determine scheme, MII category, and card specifications.",
    tags=["BIN Intelligence"]
)
def lookup_bin(bin_number: str):
    clean_bin = "".join(c for c in bin_number if c.isdigit())
    if len(clean_bin) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BIN number must be at least 4 digits."
        )
    
    # Pad to standard test length if necessary for matching
    padded = clean_bin.ljust(16, '0')
    brand_spec = detect_card_brand(padded)
    first_digit = clean_bin[0]

    return {
        "bin": clean_bin,
        "brand": brand_spec.name if brand_spec else "Unknown Scheme",
        "code": brand_spec.code if brand_spec else "UNKNOWN",
        "category": brand_spec.category if brand_spec else "Unassigned",
        "mii_industry": get_mii_description(first_digit),
        "valid_lengths": brand_spec.valid_lengths if brand_spec else [],
        "cvv_length": brand_spec.cvv_length if brand_spec else 3
    }
