"""Application configuration using Pydantic settings.

Configuration is loaded from environment variables or .env file.
Different configurations can be used for dev/staging/prod environments.
"""

import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden via environment variables.
    For example, DATABASE_URL can be set in the environment or .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    PROJECT_NAME: str = "AI Service"
    PROJECT_DESCRIPTION: str = "AI-powered content generation, translation, and automation service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8010
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Override in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://engadi.org",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_service_db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (for caching, sessions, etc.)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka (for event-driven architecture)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "ai_service"
    
    # External Services
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    CONTENT_SERVICE_URL: str = "http://localhost:8003"
    SOCIAL_MEDIA_SERVICE_URL: str = "http://localhost:8007"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8008"
    PARTNERS_CRM_SERVICE_URL: str = "http://localhost:8005"
    PROJECTS_SERVICE_URL: str = "http://localhost:8006"
    
    # Abacus.AI Configuration
    ABACUS_AI_API_KEY: Optional[str] = None  # Automatically loaded from environment
    ABACUS_AI_DEPLOYMENT_TOKEN: str = "your-deployment-token"
    ABACUS_AI_DEPLOYMENT_ID: str = "your-deployment-id"
    ABACUS_AI_API_URL: str = "https://api.abacus.ai"
    
    # AI Model Settings
    AI_DEFAULT_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    AI_TIMEOUT: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Monitoring
    DATADOG_API_KEY: Optional[str] = None
    DATADOG_APP_KEY: Optional[str] = None
    
    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    

# Create global settings instance
settings = Settings()
