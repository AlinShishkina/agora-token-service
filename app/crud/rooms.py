from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import Room
from app.schemas import RoomCreate, RoomUpdate

class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[Room]:
        return db.query(Room).filter(Room.uuid == uuid).first()
    
    def get_by_channel_name(self, db: Session, *, channel_name: str) -> Optional[Room]:
        return db.query(Room).filter(Room.agora_channel_name == channel_name).first()

room_crud = CRUDRoom(Room)