from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime,timezone
from uuid import uuid4, UUID
from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit import Unit

class Project(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[str] = None
    artwork_url: Optional[str] = None
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    units: list["Unit"] = Relationship(back_populates="project")