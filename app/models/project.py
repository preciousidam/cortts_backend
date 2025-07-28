import enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Literal, Optional, TYPE_CHECKING
from datetime import datetime,timezone
from uuid import uuid4, UUID
from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit import Unit

class ProjectPurpose(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    OTHER = "other"

class Status(str, enum.Enum):
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ONGOING = "ongoing"

class Project(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[ProjectPurpose] = None
    artwork_url: Optional[str] = None
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    units: list["Unit"] = Relationship(back_populates="project")

    @property
    def status(self) -> str:
        if self.deleted:
            return Status.ARCHIVED.value
        if self.units:
            for unit in self.units:
                if unit.handover_date == None:
                    return Status.ONGOING.value
        return Status.COMPLETED.value
