from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import TokenLog  
from app.schemas import TokenLogCreate, TokenLogUpdate  

class CRUDTokenLog(CRUDBase[TokenLog, TokenLogCreate, TokenLogUpdate]):
    def create_token_log(
        self,
        db: Session,
        *,
        user_id: str,
        channel: Optional[str],
        token_type: str,
        token_hash: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenLog:
        obj_in = TokenLogCreate(
            user_id=user_id,
            channel=channel,
            token_type=token_type,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return self.create(db, obj_in=obj_in)

token_log_crud = CRUDTokenLog(TokenLog)