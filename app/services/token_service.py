import logging
import time 
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.utils.agora_token import AgoraTokenGenerator
from app.crud.token_logs import token_log_crud
from app.config import settings

logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self, db: Session):
        self.db = db
        self.token_generator = AgoraTokenGenerator()

    def generate_rtc_token(
        self, channel: str, uid: str, role: str, user_id: str,
        ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            token_info = self.token_generator.generate_rtc_token(channel, uid, role)
            expires_at = datetime.fromtimestamp(token_info["expire_timestamp"])
            
            token_log_crud.create_token_log(
                db=self.db, user_id=user_id, channel=channel,
                token_type="rtc",
                token_hash=self.token_generator.hash_token(token_info["token"]),
                expires_at=expires_at, ip_address=ip_address, user_agent=user_agent
            )
            
            logger.info(f"RTC token: {user_id}@{channel}")
            return token_info
        except Exception as e:
            logger.error(f"Error RTC: {str(e)}")
            raise

    def generate_rtm_token(self, uid: str, user_id: str, channel: str = "", ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        try:
            token_info = self.token_generator.generate_rtm_token(uid)
            expires_at = datetime.fromtimestamp(token_info["expire_timestamp"])
            
            token_log_crud.create_token_log(
                db=self.db, user_id=user_id, channel=channel or f"rtm_{uid}",
                token_type="rtm",
                token_hash=self.token_generator.hash_token(token_info["token"]),
                expires_at=expires_at, ip_address=ip_address, user_agent=user_agent
            )
            
            logger.info(f"RTM token: {user_id}")
            return token_info
        except Exception as e:
            logger.error(f"Error RTM: {str(e)}")
            raise

    def generate_dual_tokens(self, channel: str, uid: str, role: str, user_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        try:
            rtc = self.generate_rtc_token(channel, uid, role, user_id, ip_address, user_agent)
            rtm = self.generate_rtm_token(uid, user_id, channel, ip_address, user_agent)
            
            current_time = int(time.time())  
            combined_expire = min(rtc["expire_timestamp"], rtm["expire_timestamp"])
            
            return {
                "rtc": rtc,
                "rtm": rtm,
                "app_id": settings.AGORA_APP_ID,
                "channel": channel,
                "uid": uid,
                "role": role,
                "combined_expire": combined_expire,  
                "generated_at": current_time         
            }
        except Exception as e:
            logger.error(f"Dual: {str(e)}")
            raise
