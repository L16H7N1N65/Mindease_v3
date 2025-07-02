"""
Configuration settings for the MindEase API.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─── App / Security ───────────────────────────────────────────────────────
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MindEase API"
    PROJECT_VERSION: str = Field(..., env="PROJECT_VERSION")

    # ─── Environment ──────────────────────────────────────────────────────────
    
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    TESTING: bool = Field(default=True, env="TESTING")
    RELOAD: bool = Field(default=True, env="RELOAD")
    PORT: int = Field(8000, env="PORT")
    WORKERS: int = Field(..., env="WORKERS")
    HOST: str = Field("0.0.0.0", env="HOST")
    
    # ─── FastAPI / JWT ────────────────────────────────────────────────────────
   
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # ─── CORS / Hosts ─────────────────────────────────────────────────────────
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list, env="BACKEND_CORS_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")

    # ─── Database ─────────────────────────────────────────────────────────────
    
    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    # ─── Alembic / SQLAlchemy ─────────────────────────────────────────────────
    
    DATABASE_URL: str = Field(..., env="DATABASE_URL") 
    DATABASE_POOL_SIZE: int = Field(..., env="DATABASE_POOL_SIZE") 
    DATABASE_MAX_OVERFLOW: int = Field(..., env="DATABASE_MAX_OVERFLOW")
    
      
    # ─── Rate Limiting ───────────────────────────────────────────────────────
    
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    RATE_LIMIT_CALLS: int = Field(default=100, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")

    # ─── Redis ───────────────────────────────────────────────────────────────
    
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(..., env="REDIS_PASSWORD")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # ─── Embedding / Vector Search ───────────────────────────────────────────
    
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = Field(default=384, env="EMBEDDING_DIMENSION")
    EMBEDDING_BATCH_SIZE: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    VECTOR_DIMENSION: int = Field(..., env="VECTOR_DIMENSION")

    # ─── Hugging Face / Mistral ───────────────────────────────────────────────
    
    HF_TOKEN: str = Field(..., env="HF_TOKEN")
    HF_HOME: str = Field(..., env="HF_HOME")

    MISTRAL_API_URL: AnyHttpUrl = Field(..., env="MISTRAL_API_URL")
    MISTRAL_SERVICE_URL: AnyHttpUrl = Field(..., env="MISTRAL_SERVICE_URL")
    MISTRAL_API_KEY: str = Field(..., env="MISTRAL_API_KEY")
    MISTRAL_MODEL: str = Field(..., env="MISTRAL_MODEL")
    MISTRAL_MAX_TOKENS: int = Field(..., env="MISTRAL_MAX_TOKENS")
    MISTRAL_TEMPERATURE: float = Field(..., env="MISTRAL_TEMPERATURE")

    # ─── ETL / Data ──────────────────────────────────────────────────────────
    
    DATASET_DIR: str = Field(..., env="DATASET_DIR")
    BATCH_SIZE: int = Field(..., env="BATCH_SIZE")
    DATASET_SOURCES: List[str] = Field(["RishiKompelli/TherapyDataset"], env="DATASET_SOURCES")
    ETL_MAX_WORKERS: int = Field(..., env="ETL_MAX_WORKERS")
    ETL_TIMEOUT: int = Field(..., env="ETL_TIMEOUT")
    
    # ─── File Upload ─────────────────────────────────────────────────────────
    
    MAX_UPLOAD_SIZE: str = Field(default="50MB", env="MAX_UPLOAD_SIZE")
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    ALLOWED_FILE_TYPES: List[str] = Field(default_factory=lambda: ["pdf", "txt", "docx", "csv", "json"], env="ALLOWED_FILE_TYPES")
    
    # ─── Logging ─────────────────────────────────────────────────────────────
  
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="./logs/mindease-api.log", env="LOG_FILE")
    
    # ─── Canvas for model processing ─────────────────────────────────────────
    
    CHAT_MAX_HISTORY: int = Field(default=50, env="CHAT_MAX_HISTORY")
    CHAT_CONTEXT_WINDOW: int = Field(default=4000, env="CHAT_CONTEXT_WINDOW")
    CHAT_MAX_RESPONSE_LENGTH: int = Field(default=1000, env="CHAT_MAX_RESPONSE_LENGTH")
    
    # ─── Crisis Detection ────────────────────────────────────────────────────
    
    ENABLE_CRISIS_DETECTION: bool = Field(default=True, env="ENABLE_CRISIS_DETECTION")
    CRISIS_KEYWORDS: List[str] = Field(default_factory=lambda: ["suicide", "kill myself", "end my life", "hurt myself", "self-harm"], env="CRISIS_KEYWORDS")
    SAFETY_THRESHOLD: float = Field(default=0.8, env="SAFETY_THRESHOLD")
    
    # ─── Caching / Metrics / Monitoring ────────────────────────────────────────
    
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # ─── Background Tasks (Celery) ─────────────────────────────────────────────
    
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")
    
    # ─── Organization ──────────────────────────────────────────────────────────

    DEFAULT_ORG_NAME: str = Field(default="Mindease", env="DEFAULT_ORG_NAME")
    DEFAULT_ORG_DOMAIN: str = Field(default="mindease.com", env="DEFAULT_ORG_DOMAIN")
    
    # ─── Validators ───────────────────────────────────────────────────────────
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[AnyHttpUrl]:
        if isinstance(v, str):
            v = v.strip()
            # JSON‐style list
            if v.startswith("["):
                return [AnyHttpUrl(u) for u in json.loads(v)]
            # comma‐separated
            return [AnyHttpUrl(item.strip()) for item in v.split(",")]
        return v  

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def _parse_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [item.strip() for item in v.split(",")]
        return v
    
    
    
    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        if self.SQLALCHEMY_DATABASE_URI is None:
            
            db_path = f"/{self.POSTGRES_DB}" if self.POSTGRES_DB.startswith("/") else f"/{self.POSTGRES_DB}"
            self.SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
                scheme="postgresql+psycopg2",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                path=db_path,
            )
        return self
    
    
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings