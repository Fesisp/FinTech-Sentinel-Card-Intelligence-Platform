"""
Main FastAPI Application Entrypoint.
FinTech Sentinel - Enterprise Card Intelligence & PCI Validation Platform.
"""
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router as api_router
from app.api.middleware import BankSecurityMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## 💳 FinTech Sentinel Enterprise Card Intelligence Platform
    
    A high-precision, PCI-DSS compliant Card Validation, BIN Intelligence, and Fraud Risk Scoring System designed for banking institutions and payment processing platforms.
    
    ### Key Features:
    * **ISO/IEC 7812 Compliance**: Complete Major Industry Identifier (MII) breakdown.
    * **Luhn Algorithm Mod 10 Check**: Ultra-fast checksum verification.
    * **PCI-DSS PAN Redaction & HMAC Tokenization**: Zero raw PAN logging or exposure.
    * **Fraud & Anomaly Scoring**: Shannon entropy analysis, test card pattern matching, and sequential digit detection.
    * **Multi-Brand Support**: Visa, MasterCard, American Express, Discover, Elo, Hipercard, JCB, Diners Club, UnionPay, Maestro, Mir, Aura, Cabal.
    * **High-Throughput Batch Endpoint**: Process up to 500 cards in a single API call.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration for Banking Portals & Dashboard Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bank Telemetry & Security Headers Middleware
app.add_middleware(BankSecurityMiddleware)

# Include API Endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static Files & Enterprise Web Dashboard
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "FinTech Sentinel API Operational", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
