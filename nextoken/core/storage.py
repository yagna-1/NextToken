"""
Redis storage operations for NexToken
"""

import redis
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class TokenStorage:
    """Manages token storage and revocation status using Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.token_prefix = "nextoken:"
        self.revoked_prefix = "nextoken:revoked:"
    
    def store_token_metadata(self, token_id: str, metadata: Dict[str, Any], expires_in: int) -> bool:
        """Store token metadata in Redis"""
        try:
            key = f"{self.token_prefix}{token_id}"
            metadata_json = json.dumps(metadata)
            
            # Store with expiration
            self.redis_client.setex(key, expires_in, metadata_json)
            return True
        except Exception as e:
            print(f"Error storing token metadata: {e}")
            return False
    
    def get_token_metadata(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve token metadata from Redis"""
        try:
            key = f"{self.token_prefix}{token_id}"
            metadata_json = self.redis_client.get(key)
            
            if metadata_json:
                return json.loads(metadata_json)
            return None
        except Exception as e:
            print(f"Error retrieving token metadata: {e}")
            return None
    
    def revoke_token(self, token_id: str) -> bool:
        """Mark a token as revoked"""
        try:
            # Store in revoked tokens with a long expiration (e.g., 30 days)
            revoked_key = f"{self.revoked_prefix}{token_id}"
            self.redis_client.setex(revoked_key, 30 * 24 * 3600, "revoked")
            
            # Remove from active tokens
            active_key = f"{self.token_prefix}{token_id}"
            self.redis_client.delete(active_key)
            
            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False
    
    def is_token_revoked(self, token_id: str) -> bool:
        """Check if a token is revoked"""
        try:
            revoked_key = f"{self.revoked_prefix}{token_id}"
            return self.redis_client.exists(revoked_key) > 0
        except Exception as e:
            print(f"Error checking token revocation: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens (Redis handles this automatically with TTL)"""
        # This is handled automatically by Redis TTL
        return 0
    
    def get_token_stats(self) -> Dict[str, Any]:
        """Get token statistics"""
        try:
            # Count active tokens
            active_pattern = f"{self.token_prefix}*"
            active_count = len(self.redis_client.keys(active_pattern))
            
            # Count revoked tokens
            revoked_pattern = f"{self.revoked_prefix}*"
            revoked_count = len(self.redis_client.keys(revoked_pattern))
            
            return {
                "active_tokens": active_count,
                "revoked_tokens": revoked_count,
                "total_tokens": active_count + revoked_count
            }
        except Exception as e:
            print(f"Error getting token stats: {e}")
            return {"active_tokens": 0, "revoked_tokens": 0, "total_tokens": 0}
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False


# Global storage instance
token_storage = TokenStorage() 