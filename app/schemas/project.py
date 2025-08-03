import enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.unit import UnitRead  # Assuming 'Unit' is defined in models/unit.py

class ProjectPurpose(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    OTHER = "other"

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[ProjectPurpose] = None
    artwork_url: Optional[str] = None

class ProjectRead(ProjectCreate):
    id: UUID
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    status: str | None = None  # This will be derived from the model logic
    total_revenue: float = 0.0
    sold_units: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ProjectSingle(ProjectRead):
    units: list[UnitRead] = []  # Assuming 'Unit' is defined elsewhere in the codebase

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    num_units: Optional[int] = None
    purpose: Optional[ProjectPurpose] = None
    artwork_url: Optional[str] = None

class ProjectReplace(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[ProjectPurpose] = None
    artwork_url: Optional[str] = None

class ProjectList(BaseModel):
    data: list[ProjectRead]
    total: int