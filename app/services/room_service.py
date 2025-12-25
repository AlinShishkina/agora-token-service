# app/services/room_service.py
import uuid
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.schemas import RoomCreate
from app.crud.rooms import room_crud

logger = logging.getLogger(__name__)

class RoomService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_room(self, room_data: RoomCreate, user_id: str) -> Dict[str, Any]:
        """Создание новой комнаты"""
        try:
            room_uuid = str(uuid.uuid4())
            channel_name = f"agora_channel_{uuid.uuid4().hex[:12]}"
            
            # CRUD ожидает DICT
            room_dict = {
                "uuid": room_uuid,
                "name": room_data.name,
                "agora_channel_name": channel_name,
                "is_private": room_data.is_private,
                "max_participants": room_data.max_participants,
                "created_by": user_id
            }
            
            db_room = room_crud.create(self.db, obj_in=room_dict)
            
            logger.info(f"Created room: {db_room.name} (ID: {db_room.uuid}) for user: {user_id}")
            
            return {
                "room_id": db_room.uuid,
                "channel_name": db_room.agora_channel_name,
                "name": db_room.name,
                "is_private": db_room.is_private,
                "max_participants": db_room.max_participants,
                "created_by": db_room.created_by,
                "created_at": db_room.created_at.isoformat() if db_room.created_at else None
            }
        except Exception as e:
            logger.error(f"Error creating room: {str(e)}", exc_info=True)
            raise
    
    def get_room(self, room_uuid: str) -> Dict[str, Any]:
       # получение информации о комнате по UUID
        try:
            db_room = room_crud.get_by_uuid(self.db, uuid=room_uuid)
            if not db_room:
                raise ValueError(f"Room {room_uuid} not found")
            
            return {
                "room_id": db_room.uuid,
                "channel_name": db_room.agora_channel_name,
                "name": db_room.name,
                "is_private": db_room.is_private,
                "max_participants": db_room.max_participants,
                "created_by": db_room.created_by,
                "created_at": db_room.created_at.isoformat() if db_room.created_at else None
            }
        except Exception as e:
            logger.error(f"Error getting room: {str(e)}")
            raise
