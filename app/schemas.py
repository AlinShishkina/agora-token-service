from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class AuthResponse(BaseModel):
    user_id: str = Field(..., description="Идентификатор пользователя")
    authenticated: bool = Field(..., description="Статус аутентификации")
    timestamp: datetime = Field(..., description="Временная метка")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class HealthResponse(BaseModel):
    status: str = Field(..., description="Статус сервиса: healthy|degraded|unhealthy")
    timestamp: float = Field(..., description="Unix timestamp проверки")
    database: str = Field(..., description="Статус базы данных")
    agora: str = Field(..., description="Статус Agora конфигурации")
    uptime: float = Field(..., description="Время работы сервиса (секунды)")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название комнаты")
    is_private: bool = Field(default=False, description="Приватная комната")
    max_participants: Optional[int] = Field(default=10, ge=1, le=100, description="Макс. участников")


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Новое название комнаты")
    is_private: Optional[bool] = Field(None, description="Новый статус приватности")
    max_participants: Optional[int] = Field(None, ge=1, le=100, description="Новое макс. участников")


class RoomResponse(BaseModel):
    room_id: str = Field(..., description="UUID комнаты")
    channel_name: str = Field(..., description="Agora channel name")
    name: str = Field(..., description="Название комнаты")
    is_private: bool = Field(..., description="Приватная комната")
    max_participants: int = Field(..., description="Макс. участников")
    created_by: str = Field(..., description="Создатель")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class RTCRequest(BaseModel):
    channel: str = Field(..., description="Название канала Agora")
    uid: str = Field(..., description="User ID для канала")
    role: str = Field(
        default="audience",
        description="Роль пользователя: host или audience",
        pattern="^(host|audience)$",
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['host', 'audience']:
            raise ValueError('Role must be either "host" or "audience"')
        return v


class RTMRequest(BaseModel):
    uid: str = Field(..., description="User ID для RTM")


class DualTokenRequest(BaseModel):
    channel: str = Field(..., description="Название канала Agora")
    uid: str = Field(..., description="User ID")
    role: str = Field(
        default="audience",
        description="Роль пользователя: host или audience",
        pattern="^(host|audience)$",
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['host', 'audience']:
            raise ValueError('Role must be either "host" or "audience"')
        return v

class TokenLogBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    user_id: str
    channel: Optional[str] = None
    token_type: str
    token_hash: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class TokenLogCreate(TokenLogBase):
    pass


class TokenLogUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class RTCTokenResponse(BaseModel):
    token: str = Field(..., description="Реальный Agora RTC токен")
    expires_in: int = Field(..., description="TTL в секундах")
    token_type: str = Field("rtc", description="Тип токена")
    channel: str = Field(..., description="Название канала")
    uid: str = Field(..., description="User ID")
    role: str = Field(..., description="Роль пользователя")
    app_id: Optional[str] = Field(None, description="Agora App ID")
    expire_timestamp: int = Field(..., description="Unix timestamp истечения")
    generated_at: int = Field(..., description="Unix timestamp генерации")


class RTMTokenResponse(BaseModel):
    token: str = Field(..., description="Реальный Agora RTM токен")
    expires_in: int = Field(..., description="TTL в секундах")
    token_type: str = Field("rtm", description="Тип токена")
    uid: str = Field(..., description="User ID")
    app_id: Optional[str] = Field(None, description="Agora App ID")
    expire_timestamp: int = Field(..., description="Unix timestamp истечения")
    generated_at: int = Field(..., description="Unix timestamp генерации")


class DualTokenResponse(BaseModel):
    rtc: RTCTokenResponse
    rtm: RTMTokenResponse
    app_id: str = Field(..., description="Agora App ID")
    channel: str = Field(..., description="Название канала")
    uid: str = Field(..., description="User ID")
    role: str = Field(..., description="Роль пользователя")
    combined_expire: int = Field(
        ...,
        description="Минимальный expire_timestamp из двух токенов",
    )
    generated_at: int = Field(..., description="Unix timestamp генерации")
