from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from sqlalchemy.types import JSON as SAJSON
from typing import Any, Optional, Type, cast
from datetime import datetime, timezone
from uuid import uuid4, UUID
from app.models.timestamp_mixin import TimestampMixin

class Notification(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str
    body: str
    data: Optional[dict[str, str]] = Field(default=None, sa_column=Column(SAJSON, nullable=True))  # Extra metadata (e.g. document_id, action, etc.)
    sent_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=cast(Type[Any], DateTime(timezone=True)),
    )
    read: bool = False
