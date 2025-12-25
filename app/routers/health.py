from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import logging

from app import schemas
from app.database import get_db
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


start_time = time.time()


@router.get(
    "/health",  
    response_model=schemas.HealthResponse,
    summary="Health check",
    description="Check the health status of the service"
)
async def health_check(db: Session = Depends(get_db)):
    try:
        # проверка базы данных
        db_status = "healthy"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            logger.error(f"Database health check failed: {str(e)}")
        
        # проверка Agora конфигурации
        agora_status = "healthy" if settings.AGORA_APP_ID and settings.AGORA_APP_CERTIFICATE else "unconfigured"
        
        uptime = time.time() - start_time
        
        return schemas.HealthResponse(
            status="healthy" if db_status == "healthy" and agora_status == "healthy" else "degraded",
            timestamp=time.time(),
            database=db_status,
            agora=agora_status,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return schemas.HealthResponse(
            status="unhealthy",
            timestamp=time.time(),
            database="unknown",
            agora="unknown",
            uptime=time.time() - start_time
        )