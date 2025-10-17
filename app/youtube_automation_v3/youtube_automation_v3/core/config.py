"""
Configuration Management
YouTube Automation System v2.0

Copyright (c) 2025 Saeed Alaediny. All rights reserved.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "YouTube Automation System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Database
    DATABASE_URL: str = "sqlite:///./youtube_automation.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # AI Provider Configuration
    AI_PROVIDER: str = "openai"  # openai, deepseek, ollama
    AI_MODEL: str = "gpt-3.5-turbo"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORG_ID: Optional[str] = None
    
    # DeepSeek (cost-effective alternative)
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    
    # Ollama (self-hosted, free)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # TTS Provider Configuration
    TTS_PROVIDER: str = "google"  # google, coqui, edge
    TTS_VOICE: str = "en-US-Standard-A"
    
    # Google Cloud TTS
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_PROJECT_ID: Optional[str] = None
    
    # Coqui TTS (self-hosted, free)
    COQUI_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # Storage Configuration
    STORAGE_PROVIDER: str = "local"  # local, s3, minio
    STORAGE_PATH: str = "/var/lib/youtube_automation"
    
    # S3/MinIO
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = True
    
    # YouTube API
    YOUTUBE_CREDENTIALS_PATH: Optional[str] = None
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_DEFAULT_CATEGORY: str = "22"  # People & Blogs
    YOUTUBE_DEFAULT_PRIVACY: str = "public"  # public, private, unlisted
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3300  # 55 minutes
    
    # Video Generation
    VIDEO_DEFAULT_DURATION: int = 300  # 5 minutes
    VIDEO_DEFAULT_RESOLUTION: str = "1920x1080"
    VIDEO_DEFAULT_FPS: int = 24
    VIDEO_DEFAULT_CODEC: str = "libx264"
    VIDEO_DEFAULT_AUDIO_CODEC: str = "aac"
    VIDEO_QUALITY: str = "medium"  # low, medium, high
    
    # Content Generation
    CONTENT_DEFAULT_NICHE: str = "technology"
    CONTENT_LANGUAGE: str = "en"
    CONTENT_MIN_SCRIPT_LENGTH: int = 500
    CONTENT_MAX_SCRIPT_LENGTH: int = 5000
    
    # Automation
    AUTO_UPLOAD_ENABLED: bool = False
    AUTO_GENERATION_ENABLED: bool = False
    DAILY_GENERATION_TIME: str = "09:00"
    MAX_VIDEOS_PER_DAY: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "youtube_automation.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB
    ALLOWED_EXTENSIONS: list = [".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png"]
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Feature Flags
    FEATURE_MULTI_TENANCY: bool = True
    FEATURE_PLUGINS: bool = True
    FEATURE_ANALYTICS: bool = True
    FEATURE_WEBHOOKS: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

# Global settings instance
settings = Settings()

# Helper functions
def get_ai_provider_config() -> dict:
    """Get AI provider configuration"""
    if settings.AI_PROVIDER == "openai":
        return {
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.AI_MODEL,
            "org_id": settings.OPENAI_ORG_ID
        }
    elif settings.AI_PROVIDER == "deepseek":
        return {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "model": "deepseek-chat"
        }
    elif settings.AI_PROVIDER == "ollama":
        return {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL
        }
    else:
        raise ValueError(f"Unknown AI provider: {settings.AI_PROVIDER}")

def get_tts_provider_config() -> dict:
    """Get TTS provider configuration"""
    if settings.TTS_PROVIDER == "google":
        return {
            "credentials_path": settings.GOOGLE_CREDENTIALS_PATH,
            "project_id": settings.GOOGLE_PROJECT_ID,
            "voice": settings.TTS_VOICE
        }
    elif settings.TTS_PROVIDER == "coqui":
        return {
            "model": settings.COQUI_MODEL
        }
    else:
        raise ValueError(f"Unknown TTS provider: {settings.TTS_PROVIDER}")

def get_storage_provider_config() -> dict:
    """Get storage provider configuration"""
    if settings.STORAGE_PROVIDER == "local":
        return {
            "path": settings.STORAGE_PATH
        }
    elif settings.STORAGE_PROVIDER in ["s3", "minio"]:
        return {
            "endpoint": settings.S3_ENDPOINT,
            "access_key": settings.S3_ACCESS_KEY,
            "secret_key": settings.S3_SECRET_KEY,
            "bucket": settings.S3_BUCKET,
            "region": settings.S3_REGION,
            "use_ssl": settings.S3_USE_SSL
        }
    else:
        raise ValueError(f"Unknown storage provider: {settings.STORAGE_PROVIDER}")

def is_production() -> bool:
    """Check if running in production"""
    return settings.ENVIRONMENT == "production"

def is_development() -> bool:
    """Check if running in development"""
    return settings.ENVIRONMENT == "development"
