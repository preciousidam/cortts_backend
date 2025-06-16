from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.agent import AgentType


class AgentBase(SQLModel):
    fullname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    type: AgentType
    description: Optional[str] = None
    address: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    deleted: bool
    reason_for_delete: Optional[str] = None


class AgentUpdate(SQLModel):
    fullname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    type: Optional[AgentType] = None
    description: Optional[str] = None
    address: Optional[str] = None
    deleted: Optional[bool] = None
    reason_for_delete: Optional[str] = None