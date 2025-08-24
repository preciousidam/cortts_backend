from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID

class PaymentStatus(str, Enum):
    PAID = "paid"
    NOT_PAID = "not_paid"
    OVERDUE = "overdue"

class PaymentBase(BaseModel):
    reason_for_payment: Optional[str] = 'N/A'
    amount: float
    due_date: datetime | None = None
    status: PaymentStatus = PaymentStatus.NOT_PAID
    unit_id: UUID

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    reason_for_payment: Optional[str] = None

class PaymentRead(PaymentBase):
    id: UUID
    deleted: bool
    reason_for_delete: Optional[str]
    created_at: datetime
    updated_at: datetime