from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app import schemas
from app.database import get_db
from app.utils.security import validate_user_id

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/auth",
    response_model=schemas.AuthResponse,
    summary="User authentication",
    description="Authentication using X-User-Id header"
)
async def auth_endpoint(
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    # аутентификация по заголовку X-User-Id
    try:
        logger.info(f"User authentication attempt: {x_user_id}")
        
        # валидация user_id
        if not validate_user_id(x_user_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID format"
            )
        
        return schemas.AuthResponse(
            user_id=x_user_id,
            authenticated=True,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error for user {x_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )
