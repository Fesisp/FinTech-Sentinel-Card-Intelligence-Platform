"""
Application Configuration and Environment Settings.
"""
from __future__ import annotations
import os


class Settings:
    PROJECT_NAME: str = "FinTech Sentinel Card Intelligence Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # PCI-DSS Compliance Configuration
    PCI_MASK_CHAR: str = "*"
    UNMASKED_HEAD_DIGITS: int = 6  # Show BIN
    UNMASKED_TAIL_DIGITS: int = 4  # Show last 4

    # HMAC Token Secret for Audit Log Hashing
    TOKEN_SECRET_KEY: str = os.getenv("TOKEN_SECRET_KEY", "banking-enterprise-secret-key-change-in-prod-2026")

    # Risk Scoring Thresholds
    HIGH_RISK_ENTROPY_THRESHOLD: float = 2.0


settings = Settings()
