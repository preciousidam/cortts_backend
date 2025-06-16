from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[str] = None
    artwork_url: Optional[str] = None

class ProjectRead(ProjectCreate):
    id: str
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    num_units: Optional[int] = None
    purpose: Optional[str] = None
    artwork_url: Optional[str] = None

class ProjectReplace(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    num_units: int
    purpose: Optional[str] = None
    artwork_url: Optional[str] = None