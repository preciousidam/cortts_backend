from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum
from .timestamp_mixin import TimestampMixin

class AgentRole(str, Enum):
    sales_rep = "sales_rep"
    external_agent = "external_agent"

class UnitAgentLink(SQLModel, TimestampMixin, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    unit_id: str = Field(foreign_key="unit.id")
    agent_id: str = Field(foreign_key="user.id")
    role: AgentRole = Field(default=AgentRole.sales_rep)

    unit: Optional["Unit"] = Relationship(back_populates="unit_agents")
    agent: Optional["User"] = Relationship(back_populates="unit_links")