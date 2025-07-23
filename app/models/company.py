from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User

class Company(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    # One-to-many: Company -> Users
    users: List["User"] = Relationship(back_populates="company")