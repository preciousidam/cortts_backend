from sqlmodel import SQLModel
from pydantic import BaseModel 
from typing import Optional
from uuid import UUID
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted: Optional[bool] = False
    reason_for_delete: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    deleted: Optional[bool] = None
    reason_for_delete: Optional[str] = None