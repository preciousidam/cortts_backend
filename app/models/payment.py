from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Any, Optional, TYPE_CHECKING, Type, cast
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, Numeric
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
    amount: Decimal = Field(sa_type=cast(Type[Any], Numeric(18, 2)))
    due_date: datetime | None = Field(default=None, sa_type=cast(Type[Any], DateTime(timezone=True)))
    status: PaymentStatus = PaymentStatus.NOT_PAID
    deleted: bool = False
    reason_for_delete: Optional[str] = None
    payment_date: datetime | None = Field(default=None, sa_type=cast(Type[Any], DateTime(timezone=True)))
    media_id: UUID | None = Field(default=None, foreign_key="mediafile.id")

    unit_id: UUID = Field(foreign_key="unit.id", nullable=False)
    unit: Optional["Unit"] = Relationship(back_populates="payments")
