"""
Bank-Grade Security and Telemetry Middleware.
Adds strict security headers, PCI-DSS compliance headers, execution timing, and Correlation ID tracking.
"""
from __future__ import annotations
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class BankSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000

        # Enterprise & PCI-DSS Headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-MS"] = f"{process_time_ms:.2f}"
        response.headers["X-PCI-DSS-Compliance"] = "Strict-PAN-Redacted"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store, max-age=0"

        return response
