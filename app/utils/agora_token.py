# app/utils/agora_token.py - ✅ 7/7 РАБОТАЕТ! ЧИСЛОВЫЕ РОЛИ ДЛЯ RTC+RTM!
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from agora_token_builder import RtcTokenBuilder, RtmTokenBuilder
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AgoraTokenConfig:
    app_id: str
    app_certificate: str
    rtc_token_expiry: int = 3600
    rtm_token_expiry: int = 86400
    enable_cache: bool = True
    cache_cleanup_interval: int = 300
    token_safety_margin: int = 30

class AgoraTokenGenerator:
    def __init__(self, config: Optional[AgoraTokenConfig] = None):
        if config:
            self.config = config
        else:
            self.config = AgoraTokenConfig(
                app_id=settings.AGORA_APP_ID,
                app_certificate=settings.AGORA_APP_CERTIFICATE,
                rtc_token_expiry=getattr(settings, 'AGORA_RTC_TOKEN_EXPIRY', 3600),
                rtm_token_expiry=getattr(settings, 'AGORA_RTM_TOKEN_EXPIRY', 86400)
            )
        
        self.token_cache: Dict[str, Dict[str, Any]] = {}
        self.last_cache_cleanup = time.time()
        
        if not self.config.app_id or not self.config.app_certificate:
            raise ValueError("Agora credentials are not configured")
    
    def validate_channel_name(self, channel_name: str) -> bool:
        if not channel_name or len(channel_name) > 64 or not all(c.isalnum() or c in '_-' for c in channel_name):
            raise ValueError("Invalid channel name")
        return True
    
    def validate_uid(self, uid: str) -> bool:
        if not uid or len(uid) > 64:
            raise ValueError("Invalid UID")
        return True
    
    def validate_role(self, role: str) -> bool:
        if role not in {"host", "audience", "publisher", "subscriber"}:
            raise ValueError("Invalid role")
        return True
    
    def _extract_uid_int(self, uid: str) -> int:
        if uid.isdigit():
            return int(uid)
        try:
            if '_' in uid:
                for part in reversed(uid.split('_')):
                    if part.isdigit():
                        return int(part)
        except:
            pass
        return 0
    
    def generate_rtc_token(self, channel_name: str, uid: str, role: str = "audience") -> Dict[str, Any]:
        
        try:
            self.validate_channel_name(channel_name)
            self.validate_uid(uid)
            self.validate_role(role)
            
            uid_int = self._extract_uid_int(uid)
            current_time = int(time.time())
            expire_time = current_time + self.config.rtc_token_expiry
            
            
            agora_role = 2 if role in ["host", "publisher"] else 1  # 2=Publisher, 1=Subscriber
            
            token = RtcTokenBuilder.buildTokenWithUid(
                self.config.app_id,
                self.config.app_certificate,
                channel_name,
                uid_int,
                agora_role,  
                expire_time
            )
            
            token_data = {
                "token": token,
                "expires_in": self.config.rtc_token_expiry,
                "token_type": "rtc",
                "channel": channel_name,
                "uid": uid,
                "uid_int": uid_int,
                "role": role,
                "role_numeric": agora_role,
                "expire_timestamp": expire_time,
                "generated_at": current_time,
                "app_id": self.config.app_id
            }
            
            logger.info(f"RTC: channel={channel_name}, uid={uid}, role={agora_role}")
            return token_data
            
        except Exception as e:
            logger.error(f"RTC error: {str(e)}")
            raise
    
    def generate_rtm_token(self, uid: str) -> Dict[str, Any]:

        try:
            self.validate_uid(uid)
            current_time = int(time.time())
            expire_time = current_time + self.config.rtm_token_expiry
            
            rtm_role = 1  
            
            token = RtmTokenBuilder.buildToken(
                self.config.app_id,
                self.config.app_certificate,
                uid,
                rtm_role, 
                expire_time
            )
            
            token_data = {
                "token": token,
                "expires_in": self.config.rtm_token_expiry,
                "token_type": "rtm",
                "uid": uid,
                "expire_timestamp": expire_time,
                "generated_at": current_time,
                "app_id": self.config.app_id
            }
            
            logger.info(f"RTM: uid={uid}")
            return token_data
            
        except Exception as e:
            logger.error(f"RTM error: {str(e)}")
            raise
    
    def generate_dual_tokens(self, channel_name: str, uid: str, role: str = "audience") -> Dict[str, Any]:
    # Dual RTC+RTM токены
        try:
            rtc = self.generate_rtc_token(channel_name, uid, role)
            rtm = self.generate_rtm_token(uid)
            return {
                "rtc": rtc,
                "rtm": rtm,
                "app_id": self.config.app_id,
                "channel": channel_name,
                "uid": uid,
                "role": role
            }
        except Exception as e:
            logger.error(f"Dual error: {str(e)}")
            raise
    
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
