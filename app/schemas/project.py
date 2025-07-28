import enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

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
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

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