from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app import schemas
from app.database import get_db
from app.services.room_service import RoomService
from app.dependencies import get_user_id, rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/",  
    response_model=schemas.RoomResponse,
    summary="Create room",
    description="Create a new video streaming room",
    dependencies=[Depends(rate_limit())]
)
async def create_room(
    room_data: schemas.RoomCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    try:
        room_service = RoomService(db)
        room_info = room_service.create_room(room_data, user_id)
        
        logger.info(f"Room created: {room_info['name']} for user: {user_id}")
        return room_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create room"
        )