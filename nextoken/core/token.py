"""
Core token operations for NexToken
"""

import uuid
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import cbor2

from .crypto import crypto_manager
from .storage import token_storage


class NexToken:
    """NexToken implementation with CBOR format and Ed25519 signatures"""
    
    def __init__(self):
        self.version = "1.0"
        self.algorithm = "Ed25519"
    
    def create_token(
        self,
        user_id: str,
        email: Optional[str] = None,
        expires_in: int = 3600,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Create a new NexToken
        
        Returns:
            Tuple of (token_string, token_id)
        """
        # Generate unique token ID
        token_id = str(uuid.uuid4())
        
        # Calculate timestamps
        now = int(time.time())
        expires_at = now + expires_in
        
        # Create header
        header = {
            "alg": self.algorithm,
            "typ": "NexToken",
            "ver": self.version
        }
        
        # Create payload
        payload = {
            "jti": token_id,  # JWT ID (token ID)
            "sub": user_id,   # Subject (user ID)
            "iat": now,       # Issued at
            "exp": expires_at, # Expires at
            "nbf": now        # Not before
        }
        
        # Add encrypted email if provided
        if email:
            encrypted_email = crypto_manager.encrypt_field(email)
            payload["email_enc"] = encrypted_email
        
        # Add custom claims
        if custom_claims:
            payload["custom"] = custom_claims
        
        # Create token data structure
        token_data = {
            "header": header,
            "payload": payload
        }
        
        # Encode to CBOR
        cbor_data = cbor2.dumps(token_data)
        
        # Sign the CBOR data
        signature = crypto_manager.sign_data(cbor_data)
        
        # Create final token structure
        final_token = {
            "data": cbor_data,
            "signature": signature
        }
        
        # Encode final token to CBOR and then base64
        final_cbor = cbor2.dumps(final_token)
        token_string = base64.urlsafe_b64encode(final_cbor).decode('utf-8')
        
        # Store token metadata in Redis
        metadata = {
            "user_id": user_id,
            "email": email,
            "issued_at": now,
            "expires_at": expires_at,
            "custom_claims": custom_claims
        }
        token_storage.store_token_metadata(token_id, metadata, expires_in)
        
        return token_string, token_id
    
    def verify_token(self, token_string: str) -> Dict[str, Any]:
        """
        Verify and decode a NexToken
        
        Returns:
            Dictionary with verification results
        """
        try:
            # Decode from base64
            token_bytes = base64.urlsafe_b64decode(token_string.encode('utf-8'))
            
            # Decode CBOR
            final_token = cbor2.loads(token_bytes)
            
            # Extract data and signature
            cbor_data = final_token["data"]
            signature = final_token["signature"]
            
            # Verify signature
            if not crypto_manager.verify_signature(cbor_data, signature):
                return {
                    "valid": False,
                    "error": "Invalid signature"
                }
            
            # Decode token data
            token_data = cbor2.loads(cbor_data)
            header = token_data["header"]
            payload = token_data["payload"]
            
            # Verify algorithm
            if header.get("alg") != self.algorithm:
                return {
                    "valid": False,
                    "error": "Unsupported algorithm"
                }
            
            # Check token ID
            token_id = payload.get("jti")
            if not token_id:
                return {
                    "valid": False,
                    "error": "Missing token ID"
                }
            
            # Check if token is revoked
            if token_storage.is_token_revoked(token_id):
                return {
                    "valid": False,
                    "error": "Token has been revoked"
                }
            
            # Check expiration
            current_time = int(time.time())
            exp_time = payload.get("exp", 0)
            
            if current_time > exp_time:
                return {
                    "valid": False,
                    "error": "Token has expired"
                }
            
            # Check not before
            nbf_time = payload.get("nbf", 0)
            if current_time < nbf_time:
                return {
                    "valid": False,
                    "error": "Token not yet valid"
                }
            
            # Decrypt email if present
            email = None
            if "email_enc" in payload:
                encrypted_email = payload["email_enc"]
                email = crypto_manager.decrypt_field(encrypted_email)
            
            # Prepare response
            result = {
                "valid": True,
                "user_id": payload.get("sub"),
                "email": email,
                "custom_claims": payload.get("custom"),
                "expires_at": datetime.fromtimestamp(exp_time),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0)),
                "token_id": token_id
            }
            
            return result
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Token verification failed: {str(e)}"
            }
    
    def revoke_token(self, token_string: str) -> Dict[str, Any]:
        """
        Revoke a NexToken
        
        Returns:
            Dictionary with revocation results
        """
        try:
            # First verify the token to get the token ID
            verification_result = self.verify_token(token_string)
            
            if not verification_result["valid"]:
                return {
                    "success": False,
                    "message": f"Cannot revoke invalid token: {verification_result.get('error', 'Unknown error')}"
                }
            
            token_id = verification_result.get("token_id")
            if not token_id:
                return {
                    "success": False,
                    "message": "Token ID not found"
                }
            
            # Revoke the token
            if token_storage.revoke_token(token_id):
                return {
                    "success": True,
                    "message": "Token successfully revoked"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to revoke token"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error revoking token: {str(e)}"
            }


# Global token instance
nextoken = NexToken() 