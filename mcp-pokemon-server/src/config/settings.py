"""Configuration settings for MCP Pokemon Server."""

import os
from typing import Optional

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    server_host: str = Field(default="localhost", alias="MCP_SERVER_HOST")
    server_port: int = Field(default=8000, alias="MCP_SERVER_PORT")
    
    # PokéAPI Configuration
    pokeapi_base_url: str = Field(
        default="https://pokeapi.co/api/v2", 
        alias="POKEAPI_BASE_URL"
    )
    pokeapi_timeout: int = Field(default=30, alias="POKEAPI_TIMEOUT")
    pokeapi_retries: int = Field(default=3, alias="POKEAPI_RETRIES")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Cache Configuration
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    cache_max_size: int = Field(default=1000, alias="CACHE_MAX_SIZE")
    
    # Performance Configuration
    max_concurrent_requests: int = Field(
        default=100, 
        alias="MAX_CONCURRENT_REQUESTS"
    )
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    
    # Development Configuration
    debug: bool = Field(default=False, alias="DEBUG")
    development_mode: bool = Field(default=False, alias="DEVELOPMENT_MODE")
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    
    # Security Configuration
    allowed_origins: str = Field(default="*", alias="ALLOWED_ORIGINS")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
