from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit import Unit

class PaymentStatus(str, Enum):
    PAID = "paid"
    NOT_PAID = "not_paid"
    OVERDUE = "overdue"

class Payment(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    reason_for_payment: Optional[str] = None
    amount: float
    due_date: datetime | None = None
    status: PaymentStatus = PaymentStatus.NOT_PAID
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    payment_date: datetime | None = None

    unit_id: UUID = Field(foreign_key="unit.id", nullable=False)
    unit: Optional["Unit"] = Relationship(back_populates="payments")