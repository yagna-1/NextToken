"""
Main FastAPI application for NexToken
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .api.endpoints import router
from . import __version__

# Create FastAPI app
app = FastAPI(
    title="NexToken API",
    description="A modern, secure authentication token system",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": time.time()
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["tokens"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "NexToken API",
        "version": __version__,
        "description": "A modern, secure authentication token system",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/info", tags=["info"])
async def info():
    """Detailed API information"""
    return {
        "name": "NexToken",
        "version": __version__,
        "description": "A modern, secure authentication token system that improves upon JWT",
        "features": [
            "Ed25519 elliptic curve signatures",
            "CBOR compact binary format",
            "Dynamic token revocation",
            "Encrypted payload fields",
            "Redis-based storage"
        ],
        "endpoints": {
            "issue": "POST /api/v1/issue",
            "verify": "POST /api/v1/verify", 
            "revoke": "POST /api/v1/revoke",
            "health": "GET /api/v1/health",
            "stats": "GET /api/v1/stats"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 