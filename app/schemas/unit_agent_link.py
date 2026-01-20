from sqlmodel import SQLModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, field_serializer
from datetime import datetime
from app.models.unit_agent_link import AgentRole
from uuid import UUID
from decimal import Decimal

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
    amount: Decimal
    expected_initial_payment: Decimal
    discount: Optional[Decimal] = Decimal("0")
    comments: Optional[str] = None

    @field_serializer("amount", "expected_initial_payment", "discount")
    def _serialize_decimal_fields(self, value: Decimal, _info):
        return float(value) if value is not None else value

class UnitAgentLinkRead(BaseModel):
    id: UUID
    unit_id: UUID
    agent_id: UUID
    role: AgentRole
    unit: Optional[Unit] = None
    agent: Optional[User] = None
    created_at: datetime
    updated_at: datetime
