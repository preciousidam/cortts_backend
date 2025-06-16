from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ClientBase(SQLModel):
    title: Optional[str] = None
    fullname: str
    status: str
    email: str
    address: str
    phone: str
    work_address: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: str
    created_at: datetime
    updated_at: datetime
    deleted: bool
    reason_for_delete: Optional[str] = None


class ClientUpdate(SQLModel):
    title: Optional[str] = None
    fullname: Optional[str] = None
    status: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    work_address: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    deleted: Optional[bool] = None
    reason_for_delete: Optional[str] = None