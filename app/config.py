import os
import json
from typing import List, Optional, Dict, Any, Union
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from dotenv import load_dotenv
import logging

load_dotenv()


class Settings(BaseSettings):
        
    ENVIRONMENT: str = Field(default="development", description="Режим работы: development/staging/production")
    APP_NAME: str = "Agora Token Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Режим отладки - только для разработки!")
    
    # cервер
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "agora_service"
    DB_USER: str = "agora_user"
    DB_PASSWORD: str = Field(default="", description="Пароль БД - обязателен в production!")
    
    @property
    def DATABASE_URL(self) -> str:
        # динамическое формирование URL базы данных"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_RECYCLE: int = 3600
    
  
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = Field(default="", description="Пароль Redis")
    REDIS_ENABLED: bool = True
    REDIS_DB: int = 0
    REDIS_TIMEOUT: int = 5
    
   
    AGORA_APP_ID: str = Field(default="", description="App ID")
    AGORA_APP_CERTIFICATE: str = Field(default="", description="App Certificate")
    AGORA_RTC_TOKEN_EXPIRY: int = 3600
    AGORA_RTM_TOKEN_EXPIRY: int = 86400
    AGORA_TOKEN_CACHE_ENABLED: bool = True
    AGORA_TOKEN_CACHE_TTL: int = 1800
    
    SECRET_KEY: str = Field(
        default="",
        description="Секретный ключ для подписи JWT и сессий "
    )
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = Field(default=[], description="Список валидных API ключей")
    
  
    CORS_ORIGINS: Union[str, List[str]] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: Union[str, List[str]] = ["*"]
    CORS_ALLOW_HEADERS: Union[str, List[str]] = ["*"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: str = "redis://redis:6379/1"
    

    LOG_LEVEL: str = Field(
        default="info",
        description="Уровень логирования: debug, info, warning, error, critical"
    )
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    HEALTH_CHECK_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    WORKERS: int = Field(
        default=4,
        description="Количество воркеров Gunicorn (auto = CPU * 2 + 1)"
    )
    THREADS: int = 2
    WORKER_TIMEOUT: int = 120
    KEEPALIVE: int = 5
    
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300
    CACHE_BACKEND: str = "redis"
    
    DOCS_ENABLED: bool = Field(
        default=True,
        description="Включение документации (/docs, /redoc)"
    )
    OPENAPI_URL: str = "/openapi.json"

    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                if v.strip() == "*":
                    return ["*"]
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
                return origins if origins else ["*"]
        return v
    
    @validator("CORS_ALLOW_METHODS", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [method.strip() for method in v.split(",") if method.strip()]
        return v
    
    @validator("CORS_ALLOW_HEADERS", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [header.strip() for header in v.split(",") if header.strip()]
        return v
    
    @validator("API_KEYS", pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [key.strip() for key in v.split(",") if key.strip()]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v
    
    @validator("DEBUG", always=True)
    def validate_debug(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and v:
            logging.warning("DEBUG mode is enabled in production!")
        return v
    
    @validator("AGORA_APP_ID")
    def validate_agora_app_id(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("AGORA_APP_ID is required in production!")
        return v
    
    @validator("AGORA_APP_CERTIFICATE")
    def validate_agora_certificate(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("AGORA_APP_CERTIFICATE is required in production!")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        if values.get("ENVIRONMENT") == "production":
            if not v or v in ["dev-secret-key-change-in-production", ""]:
                raise ValueError("SECRET_KEY must be set in production!")
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production!")
        return v
    
    @validator("WORKERS")
    def validate_workers(cls, v, values):
        if v == "auto":
            import multiprocessing
            return multiprocessing.cpu_count() * 2 + 1
        return v
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"



settings = Settings()


def validate_settings():
    logger = logging.getLogger(__name__)
    
    logger.info(f"Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Окружение: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    if settings.is_production():
        logger.info("PRODUCTION MODE ENABLED")
        
        critical_vars = [
            ("AGORA_APP_ID", settings.AGORA_APP_ID),
            ("AGORA_APP_CERTIFICATE", settings.AGORA_APP_CERTIFICATE),
            ("SECRET_KEY", settings.SECRET_KEY),
        ]
        
        for name, value in critical_vars:
            if not value:
                logger.critical(f"{name} не настроен для production!")
                raise ValueError(f"{name} must be properly configured for production!")
        
        if settings.CORS_ORIGINS == ["*"]:
            logger.warning("! CORS разрешен для всех доменов (*)")
        
        if settings.DEBUG:
            logger.warning("! DEBUG mode включен в production!")
    
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"Workers: {settings.WORKERS}")
    
    return settings