"""
FastAPI endpoints for NexToken
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..models.schemas import (
    TokenIssueRequest,
    TokenIssueResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
    TokenRevokeRequest,
    TokenRevokeResponse,
    HealthResponse
)
from ..core.token import nextoken
from ..core.storage import token_storage
from .. import __version__

router = APIRouter()


@router.post("/issue", response_model=TokenIssueResponse)
async def issue_token(request: TokenIssueRequest):
    """Issue a new NexToken"""
    try:
        token_string, token_id = nextoken.create_token(
            user_id=request.user_id,
            email=request.email,
            expires_in=request.expires_in,
            custom_claims=request.custom_claims
        )
        
        # Calculate expiration datetime
        expires_at = datetime.fromtimestamp(
            datetime.now().timestamp() + request.expires_in
        )
        
        return TokenIssueResponse(
            token=token_string,
            token_id=token_id,
            expires_at=expires_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to issue token: {str(e)}")


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(request: TokenVerifyRequest):
    """Verify a NexToken"""
    try:
        result = nextoken.verify_token(request.token)
        
        if result["valid"]:
            return TokenVerifyResponse(
                valid=True,
                user_id=result.get("user_id"),
                email=result.get("email"),
                custom_claims=result.get("custom_claims"),
                expires_at=result.get("expires_at"),
                issued_at=result.get("issued_at")
            )
        else:
            return TokenVerifyResponse(
                valid=False,
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify token: {str(e)}")


@router.post("/revoke", response_model=TokenRevokeResponse)
async def revoke_token(request: TokenRevokeRequest):
    """Revoke a NexToken"""
    try:
        result = nextoken.revoke_token(request.token)
        
        return TokenRevokeResponse(
            success=result["success"],
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke token: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_healthy = token_storage.health_check()
        
        status = "healthy" if redis_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            version=__version__,
            timestamp=datetime.now()
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version=__version__,
            timestamp=datetime.now()
        )


@router.get("/stats")
async def get_stats():
    """Get token statistics"""
    try:
        stats = token_storage.get_token_stats()
        return {
            "active_tokens": stats["active_tokens"],
            "revoked_tokens": stats["revoked_tokens"],
            "total_tokens": stats["total_tokens"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") 