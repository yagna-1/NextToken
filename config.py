"""
Configuration settings for NexToken
"""

import os
from typing import Optional


class Config:
    """Configuration class for NexToken"""
    
    # API Settings
    API_TITLE = "NexToken API"
    API_DESCRIPTION = "A modern, secure authentication token system"
    API_VERSION = "0.1.0"
    
    # Server Settings
    HOST = os.getenv("NEXTOKEN_HOST", "0.0.0.0")
    PORT = int(os.getenv("NEXTOKEN_PORT", "8000"))
    DEBUG = os.getenv("NEXTOKEN_DEBUG", "false").lower() == "true"
    
    # Redis Settings
    REDIS_URL = os.getenv("NEXTOKEN_REDIS_URL", "redis://localhost:6379")
    REDIS_DB = int(os.getenv("NEXTOKEN_REDIS_DB", "0"))
    
    # Token Settings
    DEFAULT_TOKEN_EXPIRY = int(os.getenv("NEXTOKEN_DEFAULT_EXPIRY", "3600"))  # 1 hour
    MAX_TOKEN_EXPIRY = int(os.getenv("NEXTOKEN_MAX_EXPIRY", "86400"))  # 24 hours
    REVOKED_TOKEN_RETENTION = int(os.getenv("NEXTOKEN_REVOKED_RETENTION", "2592000"))  # 30 days
    
    # Security Settings
    ALLOWED_ORIGINS = os.getenv("NEXTOKEN_ALLOWED_ORIGINS", "*").split(",")
    
    # Logging Settings
    LOG_LEVEL = os.getenv("NEXTOKEN_LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_redis_config(cls) -> dict:
        """Get Redis configuration"""
        return {
            "url": cls.REDIS_URL,
            "db": cls.REDIS_DB,
        }
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": cls.ALLOWED_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


# Development configuration
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Production configuration
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ALLOWED_ORIGINS = ["https://yourdomain.com"]  # Configure appropriately


# Testing configuration
class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    REDIS_URL = "redis://localhost:6379/1"  # Use different DB for testing


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(environment: Optional[str] = None) -> Config:
    """Get configuration for the specified environment"""
    if environment is None:
        environment = os.getenv("NEXTOKEN_ENV", "development")
    
    return config_map.get(environment, DevelopmentConfig) 