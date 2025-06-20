from sqlmodel import SQLModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PushTokenBase(SQLModel):
    token: str
    device: Optional[str] = None

class PushTokenCreate(PushTokenBase):
    user_id: UUID

class PushTokenRead(PushTokenBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime