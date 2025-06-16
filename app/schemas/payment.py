from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID

class PaymentStatus(str, Enum):
    paid = "paid"
    not_paid = "not paid"
    over_due = "over due"

class PaymentBase(BaseModel):
    amount: float
    due_date: datetime
    status: PaymentStatus = PaymentStatus.not_paid
    unit_id: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    status: Optional[PaymentStatus] = None

class PaymentRead(PaymentBase):
    id: UUID
    deleted: bool
    reason_for_delete: Optional[str]