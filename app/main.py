import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.database import engine, Base
from app.utils.logger import setup_logging
from app.config import settings

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting application...")
    
    # cоздание таблиц в БД при старте
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
    
    yield
    
    logger.info("Shutting down application...")



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Микросервис для генерации токенов Agora",
    docs_url="/docs" if (settings.DEBUG or getattr(settings, 'DOCS_ENABLED', True)) else None,
    redoc_url="/redoc" if (settings.DEBUG or getattr(settings, 'DOCS_ENABLED', True)) else None,
    openapi_url="/openapi.json" if (settings.DEBUG or getattr(settings, 'DOCS_ENABLED', True)) else None,
    lifespan=lifespan,
)

# middleware для CORS
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=getattr(settings, 'CORS_ALLOW_CREDENTIALS', True),
        allow_methods=getattr(settings, 'CORS_ALLOW_METHODS', ["*"]),
        allow_headers=getattr(settings, 'CORS_ALLOW_HEADERS', ["*"]),
    )

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=getattr(settings, 'ALLOWED_HOSTS', ["*"])
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    if request.url.path not in ["/health", "/health/", "/healthcheck"]:
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
    
    try:
        response = await call_next(request)
    except Exception as exc:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} | "
            f"Duration: {process_time:.3f}s | Error: {str(exc)}"
        )
        raise
    
    process_time = time.time() - start_time
    
    if request.url.path not in ["/health", "/health/", "/healthcheck"]:
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.3f}s"
        )
    
    return response



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"HTTP error: {exc.status_code} - {exc.detail} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation error: {exc.errors()} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "status_code": 422
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error: {str(exc)} | "
        f"Path: {request.url.path} | Method: {request.method}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        },
    )


# импорт роутов
try:
    from app.routers.auth import router as auth_router
    from app.routers.tokens import router as tokens_router
    from app.routers.rooms import router as rooms_router
    from app.routers.health import router as health_router
    
    app.include_router(auth_router, prefix="/api", tags=["Authentication"])
    app.include_router(tokens_router, prefix="/api/tokens", tags=["Tokens"])
    app.include_router(rooms_router, prefix="/api/rooms", tags=["Rooms"])
    app.include_router(health_router, tags=["Health"])
    
    logger.info("All routers imported and mounted successfully")
    
except ImportError as e:
    logger.error(f"Failed to import routers: {str(e)}")
    raise



@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if (settings.DEBUG or getattr(settings, 'DOCS_ENABLED', True)) else None,
        "health": "/health"
    }



@app.get("/healthcheck")
async def healthcheck_compatibility():
    from app.database import SessionLocal
    from sqlalchemy import text
    import time
    
    try:
        # используем сессию для проверки БД
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        finally:
            db.close()
        
        # проверка Agora конфигурации
        agora_status = "healthy" if settings.AGORA_APP_ID and settings.AGORA_APP_CERTIFICATE else "unconfigured"
        
        return {
            "status": "healthy" if db_status == "healthy" and agora_status == "healthy" else "degraded",
            "timestamp": time.time(),
            "database": db_status,
            "agora": agora_status,
            "uptime": time.time() - app_start_time
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "database": "unknown",
            "agora": "unknown",
            "error": str(e)
        }


app_start_time = time.time()