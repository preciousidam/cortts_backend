from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime, timezone
from app.models.timestamp_mixin import TimestampMixin


class DocumentTemplate(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    link: str
    unit_id: UUID = Field(foreign_key="unit.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None


class SignedDocument(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    link: str
    unit_id: UUID = Field(foreign_key="unit.id")
    client_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    agent_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None