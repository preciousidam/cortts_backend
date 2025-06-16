from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime, timezone

class Role(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CLIENT = "client"

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fullname: str
    email: str = Field(index=True, unique=True)
    phone: str = Field(index=True, unique=True)
    hashed_password: str
    address: Optional[str] = None
    role: Role = Field(default=Role.CLIENT)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    commission_rate: Optional[float] = None
    is_internal: Optional[bool] = None
    created_by: Optional[UUID] = Field(default=None, foreign_key="user.id")

    # As a client (owns one or more units)
    units: list["Unit"] = Relationship(back_populates="client")

    # As an agent (linked via association table)
    unit_links: list["UnitAgentLink"] = Relationship(back_populates="agent")

