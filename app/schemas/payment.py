from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, field_serializer

class PaymentStatus(str, Enum):
    PAID = "paid"
    NOT_PAID = "not_paid"
    OVERDUE = "overdue"

class Unit(BaseModel):
    id: UUID
    name: str

class PaymentBase(BaseModel):
    reason_for_payment: Optional[str] = 'N/A'
    amount: Decimal
    due_date: datetime | None = None
    status: PaymentStatus = PaymentStatus.NOT_PAID
    payment_date: datetime | None = None
    unit_id: UUID
    media_id: UUID | None = None
    @field_serializer("amount")
    def _serialize_amount(self, value: Decimal, _info):
        return float(value) if value is not None else value

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    reason_for_payment: Optional[str] = None
    media_id: UUID | None = None

class PaymentRead(PaymentBase):
    id: UUID
    deleted: bool
    unit: Unit
    created_at: datetime
    updated_at: datetime

class AllPayment(BaseModel):
    data: list[PaymentRead]
    total: int
