from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone
from app.models.timestamp_mixin import TimestampMixin


class DocumentTemplate(SQLModel, TimestampMixin, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    link: str
    unit_id: str = Field(foreign_key="unit.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None


class SignedDocument(SQLModel, TimestampMixin, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    link: str
    unit_id: str = Field(foreign_key="unit.id")
    client_id: Optional[str] = Field(default=None, foreign_key="client.id")
    agent_id: Optional[str] = Field(default=None, foreign_key="agent.id")
    deleted: bool = False
    reason_for_delete: Optional[str] = None