from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from app.models.unit_agent_link import AgentRole


class UnitAgentLinkBase(SQLModel):
    unit_id: str
    agent_id: str
    role: str


class UnitAgentLinkCreate(UnitAgentLinkBase):
    pass




class UnitAgentLinkRead(BaseModel):
    id: str
    unit_id: str
    agent_id: str
    role: AgentRole
    created_at: datetime
    updated_at: datetime