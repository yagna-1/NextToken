"""
Unit tests for NexToken
"""

import pytest
import time
from datetime import datetime, timedelta

from nextoken.core.token import nextoken
from nextoken.core.crypto import crypto_manager
from nextoken.core.storage import token_storage


class TestNexToken:
    """Test cases for NexToken functionality"""
    
    def test_create_token_basic(self):
        """Test basic token creation"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            expires_in=3600
        )
        
        assert token_string is not None
        assert token_id is not None
        assert len(token_string) > 0
        assert len(token_id) > 0
    
    def test_create_token_with_email(self):
        """Test token creation with encrypted email"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            email="test@example.com",
            expires_in=3600
        )
        
        assert token_string is not None
        assert token_id is not None
        
        # Verify the token
        result = nextoken.verify_token(token_string)
        assert result["valid"] is True
        assert result["user_id"] == "test_user"
        assert result["email"] == "test@example.com"
    
    def test_create_token_with_custom_claims(self):
        """Test token creation with custom claims"""
        custom_claims = {"role": "admin", "permissions": ["read", "write"]}
        
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            custom_claims=custom_claims,
            expires_in=3600
        )
        
        assert token_string is not None
        
        # Verify the token
        result = nextoken.verify_token(token_string)
        assert result["valid"] is True
        assert result["user_id"] == "test_user"
        assert result["custom_claims"] == custom_claims
    
    def test_verify_valid_token(self):
        """Test verification of a valid token"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            expires_in=3600
        )
        
        result = nextoken.verify_token(token_string)
        assert result["valid"] is True
        assert result["user_id"] == "test_user"
        assert result["token_id"] == token_id
    
    def test_verify_expired_token(self):
        """Test verification of an expired token"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            expires_in=1  # 1 second expiration
        )
        
        # Wait for token to expire
        time.sleep(2)
        
        result = nextoken.verify_token(token_string)
        assert result["valid"] is False
        assert "expired" in result["error"].lower()
    
    def test_verify_invalid_token(self):
        """Test verification of an invalid token"""
        result = nextoken.verify_token("invalid_token_string")
        assert result["valid"] is False
        assert "error" in result
    
    def test_revoke_token(self):
        """Test token revocation"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            expires_in=3600
        )
        
        # Verify token is valid initially
        result = nextoken.verify_token(token_string)
        assert result["valid"] is True
        
        # Revoke the token
        revoke_result = nextoken.revoke_token(token_string)
        assert revoke_result["success"] is True
        
        # Verify token is now invalid
        result = nextoken.verify_token(token_string)
        assert result["valid"] is False
        assert "revoked" in result["error"].lower()
    
    def test_revoke_invalid_token(self):
        """Test revoking an invalid token"""
        result = nextoken.revoke_token("invalid_token")
        assert result["success"] is False
        assert "error" in result["message"]
    
    def test_crypto_operations(self):
        """Test cryptographic operations"""
        # Test encryption/decryption
        test_email = "test@example.com"
        encrypted = crypto_manager.encrypt_field(test_email)
        decrypted = crypto_manager.decrypt_field(encrypted)
        
        assert encrypted != test_email  # Should be encrypted
        assert decrypted == test_email  # Should decrypt correctly
        
        # Test signature verification
        test_data = b"test_data"
        signature = crypto_manager.sign_data(test_data)
        assert crypto_manager.verify_signature(test_data, signature) is True
        
        # Test invalid signature
        assert crypto_manager.verify_signature(test_data, b"invalid_signature") is False
    
    def test_storage_operations(self):
        """Test storage operations"""
        # Test storing and retrieving metadata
        token_id = "test_token_123"
        metadata = {
            "user_id": "test_user",
            "email": "test@example.com",
            "issued_at": int(time.time()),
            "expires_at": int(time.time()) + 3600
        }
        
        # Store metadata
        success = token_storage.store_token_metadata(token_id, metadata, 3600)
        assert success is True
        
        # Retrieve metadata
        retrieved = token_storage.get_token_metadata(token_id)
        assert retrieved is not None
        assert retrieved["user_id"] == metadata["user_id"]
        assert retrieved["email"] == metadata["email"]
        
        # Test revocation
        success = token_storage.revoke_token(token_id)
        assert success is True
        
        # Check if revoked
        is_revoked = token_storage.is_token_revoked(token_id)
        assert is_revoked is True
    
    def test_token_structure(self):
        """Test that tokens have the correct structure"""
        token_string, token_id = nextoken.create_token(
            user_id="test_user",
            email="test@example.com",
            expires_in=3600
        )
        
        # Verify token structure by decoding
        result = nextoken.verify_token(token_string)
        assert result["valid"] is True
        assert result["user_id"] == "test_user"
        assert result["email"] == "test@example.com"
        assert result["token_id"] == token_id
        assert result["expires_at"] is not None
        assert result["issued_at"] is not None
    
    def test_multiple_tokens(self):
        """Test creating and managing multiple tokens"""
        # Create multiple tokens
        tokens = []
        for i in range(3):
            token_string, token_id = nextoken.create_token(
                user_id=f"user_{i}",
                email=f"user{i}@example.com",
                expires_in=3600
            )
            tokens.append((token_string, token_id))
        
        # Verify all tokens
        for token_string, token_id in tokens:
            result = nextoken.verify_token(token_string)
            assert result["valid"] is True
            assert result["token_id"] == token_id
        
        # Revoke one token
        token_to_revoke, token_id_to_revoke = tokens[0]
        revoke_result = nextoken.revoke_token(token_to_revoke)
        assert revoke_result["success"] is True
        
        # Verify revoked token is invalid
        result = nextoken.verify_token(token_to_revoke)
        assert result["valid"] is False
        
        # Verify other tokens are still valid
        for token_string, token_id in tokens[1:]:
            result = nextoken.verify_token(token_string)
            assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__]) 