from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime, timezone
from enum import Enum
from .timestamp_mixin import TimestampMixin
from .unit import Unit
from .user import User

class AgentRole(str, Enum):
    sales_rep = "sales_rep"
    external_agent = "external_agent"

class UnitAgentLink(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    unit_id: UUID = Field(foreign_key="unit.id")
    agent_id: UUID = Field(foreign_key="user.id")
    role: AgentRole = Field(default=AgentRole.sales_rep)

    unit: Optional["Unit"] = Relationship(back_populates="unit_agents")
    agent: Optional["User"] = Relationship(back_populates="unit_links")