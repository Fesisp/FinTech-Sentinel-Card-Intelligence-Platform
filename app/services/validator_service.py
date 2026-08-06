"""
Enterprise Card Validation Service.
Combines core domain logic, security tokenization, and risk evaluation.
"""
from __future__ import annotations
from typing import List
from app.core.luhn import clean_card_number, validate_luhn
from app.core.brands import detect_card_brand
from app.core.security import mask_card_number, generate_card_token, evaluate_fraud_risk
from app.domain.models import (
    CardValidationResponse,
    RiskAssessment,
    BatchValidationResponse
)


class CardValidatorService:
    @staticmethod
    def validate_card(card_number: str, include_risk: bool = True) -> CardValidationResponse:
        clean = clean_card_number(card_number)
        is_luhn_ok = validate_luhn(clean)
        brand_spec = detect_card_brand(clean)

        brand_name = brand_spec.name if brand_spec else "Unknown Brand"
        brand_code = brand_spec.code if brand_spec else "UNKNOWN"
        category = brand_spec.category if brand_spec else "Unassigned"
        mii_industry = brand_spec.mii_industry if brand_spec else "Unknown"
        cvv_len = brand_spec.cvv_length if brand_spec else 3

        masked = mask_card_number(clean)
        bin_number = clean[:6] if len(clean) >= 6 else clean
        last_four = clean[-4:] if len(clean) >= 4 else clean
        card_token = generate_card_token(clean)

        risk_details = None
        if include_risk:
            risk_raw = evaluate_fraud_risk(clean, is_luhn_ok, brand_name)
            risk_details = RiskAssessment(
                score=risk_raw["score"],
                level=risk_raw["level"],
                flags=risk_raw["flags"],
                entropy=risk_raw["entropy"]
            )

        return CardValidationResponse(
            masked_card=masked,
            bin=bin_number,
            last_four=last_four,
            is_valid_luhn=is_luhn_ok,
            brand=brand_name,
            brand_code=brand_code,
            category=category,
            mii_industry=mii_industry,
            cvv_length=cvv_len,
            card_token=card_token,
            risk_assessment=risk_details
        )

    @classmethod
    def validate_batch(cls, card_numbers: List[str]) -> BatchValidationResponse:
        results: List[CardValidationResponse] = []
        valid_count = 0
        invalid_count = 0
        high_risk_count = 0

        for num in card_numbers:
            res = cls.validate_card(num, include_risk=True)
            results.append(res)
            if res.is_valid_luhn and res.brand != "Unknown Brand":
                valid_count += 1
            else:
                invalid_count += 1

            if res.risk_assessment and res.risk_assessment.level in ("HIGH", "CRITICAL"):
                high_risk_count += 1

        return BatchValidationResponse(
            total_processed=len(card_numbers),
            valid_count=valid_count,
            invalid_count=invalid_count,
            high_risk_count=high_risk_count,
            results=results
        )
