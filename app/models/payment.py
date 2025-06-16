from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from datetime import datetime
from uuid import uuid4, UUID
from app.models.timestamp_mixin import TimestampMixin

class PaymentStatus(str, Enum):
    paid = "paid"
    not_paid = "not paid"
    over_due = "over due"

class Payment(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    amount: float
    due_date: datetime
    status: PaymentStatus = PaymentStatus.not_paid
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    unit_id: UUID = Field(foreign_key="unit.id")
    unit: Optional["Unit"] = Relationship(back_populates="payments")