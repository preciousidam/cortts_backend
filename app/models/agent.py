from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from enum import Enum
from app.models.timestamp_mixin import TimestampMixin


class AgentType(str, Enum):
    internal = "internal"
    external = "external"


class Agent(SQLModel, TimestampMixin, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    fullname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    type: AgentType
    description: Optional[str] = None
    address: Optional[str] = None
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    agent_units: List["UnitAgentLink"] = Relationship(back_populates="agent")