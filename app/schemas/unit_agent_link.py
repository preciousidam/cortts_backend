from sqlmodel import SQLModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from app.models.unit_agent_link import AgentRole
from uuid import UUID

class UnitAgentLinkBase(SQLModel):
    unit_id: UUID
    agent_id: UUID
    role: str


class UnitAgentLinkCreate(UnitAgentLinkBase):
    pass


class User(BaseModel):
    id: UUID
    username: str
    email: str

class Unit(BaseModel):
    id: UUID
    name: str
    amount: float
    expected_initial_payment: float
    discount: Optional[float] = 0
    comments: Optional[str] = None

class UnitAgentLinkRead(BaseModel):
    id: UUID
    unit_id: UUID
    agent_id: UUID
    role: AgentRole
    unit: Optional[Unit] = None
    agent: Optional[User] = None
    created_at: datetime
    updated_at: datetime