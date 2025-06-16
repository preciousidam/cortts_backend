from sqlmodel import SQLModel
from typing import Optional
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




class UnitAgentLinkRead(BaseModel):
    id: UUID
    unit_id: UUID
    agent_id: UUID
    role: AgentRole
    created_at: datetime
    updated_at: datetime