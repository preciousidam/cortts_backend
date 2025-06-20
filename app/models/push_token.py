from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID
from app.models.timestamp_mixin import TimestampMixin
from datetime import datetime, timezone

class PushToken(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    token: str  # Expo push token, FCM token, etc.
    device: str  # Optional: e.g. "iPhone 15", "Web", "Samsung S21"