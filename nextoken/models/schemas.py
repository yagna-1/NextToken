"""
Pydantic schemas for NexToken API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TokenIssueRequest(BaseModel):
    """Request model for token issuance"""
    user_id: str = Field(..., description="User identifier")
    email: Optional[str] = Field(None, description="User email (will be encrypted)")
    expires_in: int = Field(3600, description="Token expiration time in seconds")
    custom_claims: Optional[Dict[str, Any]] = Field(None, description="Additional custom claims")


class TokenIssueResponse(BaseModel):
    """Response model for token issuance"""
    token: str = Field(..., description="The generated NexToken")
    token_id: str = Field(..., description="Unique token identifier")
    expires_at: datetime = Field(..., description="Token expiration timestamp")


class TokenVerifyRequest(BaseModel):
    """Request model for token verification"""
    token: str = Field(..., description="The NexToken to verify")


class TokenVerifyResponse(BaseModel):
    """Response model for token verification"""
    valid: bool = Field(..., description="Whether the token is valid")
    user_id: Optional[str] = Field(None, description="User identifier from token")
    email: Optional[str] = Field(None, description="User email (if provided and decrypted)")
    custom_claims: Optional[Dict[str, Any]] = Field(None, description="Custom claims from token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    issued_at: Optional[datetime] = Field(None, description="Token issuance timestamp")
    error: Optional[str] = Field(None, description="Error message if token is invalid")


class TokenRevokeRequest(BaseModel):
    """Request model for token revocation"""
    token: str = Field(..., description="The NexToken to revoke")


class TokenRevokeResponse(BaseModel):
    """Response model for token revocation"""
    success: bool = Field(..., description="Whether the token was successfully revoked")
    message: str = Field(..., description="Response message")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="NexToken version")
    timestamp: datetime = Field(..., description="Current timestamp") 