from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import logging

from app import schemas
from app.database import get_db
from app.services.token_service import TokenService
from app.dependencies import get_user_id, rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/rtc",
    response_model=schemas.RTCTokenResponse,
    summary="Generate RTC token",
    description="Generate Agora RTC token for video streaming",
    dependencies=[Depends(rate_limit())]
)
async def generate_rtc_token(
    request: Request,
    token_data: schemas.RTCRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    try:
        token_service = TokenService(db)
        
        token_info = token_service.generate_rtc_token(
            channel=token_data.channel,
            uid=token_data.uid,
            role=token_data.role,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return token_info
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/rtm",
    response_model=schemas.RTMTokenResponse,
    summary="Generate RTM token",
    description="Generate Agora RTM token for real-time messaging",
    dependencies=[Depends(rate_limit())]
)
async def generate_rtm_token(
    request: Request,
    token_data: schemas.RTMRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    try:
        token_service = TokenService(db)
        
        token_info = token_service.generate_rtm_token(
            uid=token_data.uid,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return token_info
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/dual",
    response_model=schemas.DualTokenResponse,
    summary="Generate dual tokens (RTC + RTM)",
    description="Generate both RTC and RTM tokens in one request",
    dependencies=[Depends(rate_limit())]
)
async def generate_dual_tokens(
    request: Request,
    token_data: schemas.DualTokenRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    try:
        token_service = TokenService(db)
        
        tokens_info = token_service.generate_dual_tokens(
            channel=token_data.channel,
            uid=token_data.uid,
            role=token_data.role,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return tokens_info
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )