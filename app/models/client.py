from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from app.models.timestamp_mixin import TimestampMixin


class Client(SQLModel, TimestampMixin, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
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
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    units: List["Unit"] = Relationship(back_populates="client")