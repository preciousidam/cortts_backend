from sqlmodel import SQLModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class NotificationBase(SQLModel):
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    read: bool = False

class NotificationCreate(NotificationBase):
    user_id: UUID

class NotificationRead(NotificationBase):
    id: UUID
    user_id: UUID
    sent_at: datetime
    created_at: datetime
    updated_at: datetime

class NotificationList(SQLModel):
    data: list[NotificationRead]
    total: int