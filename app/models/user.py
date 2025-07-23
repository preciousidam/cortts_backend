from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime, timezone
from app.models.company import Company

from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit import Unit
    from app.models.unit_agent_link import UnitAgentLink

class Role(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CLIENT = "client"

class User(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fullname: str
    email: str = Field(index=True, unique=True)
    phone: str | None = Field(index=True, unique=True)
    hashed_password: str
    address: Optional[str] = None
    role: Role = Field(default=Role.CLIENT)
    is_verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    commission_rate: Optional[float] = None
    is_internal: Optional[bool] = None
    created_by: Optional[UUID] = Field(default=None, foreign_key="user.id")
    deleted: bool = Field(default=False)
    is_active: bool = Field(default=True)
    reason_for_delete: Optional[str] = None

    # As a client (owns one or more units)
    units: list["Unit"] = Relationship(back_populates="client")

    # As an agent (linked via association table)
    unit_links: list["UnitAgentLink"] = Relationship(back_populates="agent")
    company_id: Optional[UUID] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="users")

