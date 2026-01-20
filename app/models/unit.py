from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any, TYPE_CHECKING, Type, cast
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, Numeric

from app.models.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from app.models.unit_agent_link import UnitAgentLink
    from app.models.user import User
    from app.models.project import Project
    from app.models.payment import Payment
    from app.models.document import MediaFile

class PaymentStatus(str, Enum):
    PAID = "paid"
    NOT_PAID = "not_paid"
    OVERDUE = "overdue"

class UnitCompletionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

from enum import Enum

class PropertyType(str, Enum):
    DETACHED = "detached"
    SEMI_DETACHED = "semi_detached"
    TERRACED = "terraced"
    END_OF_TERRACE = "end_of_terrace"
    BUNGALOW = "bungalow"
    MAISONETTE = "maisonette"
    FLAT = "flat"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    PENTHOUSE = "penthouse"
    STUDIO = "studio"
    COTTAGE = "cottage"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    CHALET = "chalet"

class PaymentDuration(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BI_ANNUALLY = "bi_annually"
    ANNUALLY = "annually"

class Status(str, Enum):
    SOLD = "sold"
    AVAILABLE = "available"
    UNDER_OFFER = "under_offer"
    DELETED = "deleted"

class Unit(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    amount: Decimal = Field(sa_type=cast(Type[Any], Numeric(18, 2)))
    expected_initial_payment: Decimal = Field(sa_type=cast(Type[Any], Numeric(18, 2)))
    discount: Decimal = Field(default=Decimal("0"), sa_type=cast(Type[Any], Numeric(6, 2)))
    comments: Optional[str] = None
    type: Optional[PropertyType] = None
    purchase_date: datetime | None = Field(default=None, sa_type=cast(Type[Any], DateTime(timezone=True)))
    installment: int = 1
    payment_plan: bool = False
    client_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    project_id: Optional[UUID] = Field(default=None, foreign_key="project.id")
    media_files: List["MediaFile"] = Relationship(back_populates="unit")
    handover_date: Optional[datetime] = Field(default=None, sa_type=cast(Type[Any], DateTime(timezone=True)))
    payment_duration: PaymentDuration | None = PaymentDuration.MONTHLY
    deleted: bool | None = False
    reason_for_delete: Optional[str] | None = None
    development_status: UnitCompletionStatus | None = UnitCompletionStatus.NOT_STARTED
    warranty_period: Optional[int] | None = 12 # in months
    unit_agents: List["UnitAgentLink"] = Relationship(back_populates="unit")
    client: Optional["User"] = Relationship(back_populates="units")
    project: Optional["Project"] = Relationship(back_populates="units")
    payments: List["Payment"] = Relationship(back_populates="unit")

    @property
    def images(self) -> List[str]:
        return [media.file_path for media in self.media_files if media.file_type == "image/jpeg" or media.file_type == "image/png" or media.file_type == "image/jpg"]

    @property
    def warranty(self) -> Optional[Dict[str, Any]]:
        if not self.handover_date:
            return None
        warranty_end = self.handover_date + timedelta(days=(self.warranty_period or 0) * 30)
        return { "expire_at": warranty_end.strftime("%Y-%m-%dT%H:%M:%S%z"), "isValid": date.today() <= warranty_end.date() } if warranty_end else None

    @property
    def payment_summary(self) -> Dict[str, Any]:

        def q(val: Decimal) -> Decimal:
            return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total = self.amount - (self.amount * self.discount / Decimal("100"))
        total_deposit = Decimal(self.total_paid)
        outstanding = total - total_deposit - self.expected_initial_payment
        total_sch = self.installment
        installment_amount = q(max(outstanding, Decimal("0")) / Decimal(total_sch)) if total_sch else Decimal("0")

        percentage_paid = q((total_deposit / total) * Decimal("100")) if total else Decimal("0")
        percentage_unpaid = max(Decimal("0"), Decimal("100") - percentage_paid)
        balanced = outstanding <= Decimal("0")
        more_or_less = "equal"
        installment_diff = Decimal("0.00")

        if outstanding < Decimal("0"):
            more_or_less = "overpaid"
            installment_diff = abs(outstanding)
        elif outstanding > Decimal("0"):
            more_or_less = "underpaid"
            installment_diff = outstanding

        return {
            "total": float(q(total)),
            "outstanding": float(q(outstanding)),
            "total_deposit": float(q(total_deposit)),
            "total_unpaid": float(q(total - total_deposit)),
            "balanced": balanced,
            "more_or_less": more_or_less,
            "percentage_paid": float(q(percentage_paid)),
            "percentage_unpaid": float(q(percentage_unpaid)),
            "installment_amount": float(q(installment_amount)),
            "total_sch": total_sch,
            "installment_diff": float(q(installment_diff)),
            "duration": self.payment_duration.value if self.payment_duration else None
        }

    @property
    def graph_data(self) -> List[Dict[str, float | int]]:
        if not self.installment:
            return []
        total = self.amount - self.discount
        balance = total - self.expected_initial_payment
        monthly_payment = balance / Decimal(self.installment)
        return [
            {"month": i + 1, "amount": float(monthly_payment.quantize(Decimal("0.01")))}
            for i in range(self.installment)
        ]

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments if p.status.value == PaymentStatus.PAID)

    @property
    def status(self) -> Status:
        # Determine if unit is sold, available, or under offer
        if self.client_id and not self.deleted:
            return Status.SOLD
        elif not self.client_id and not self.deleted:
            return Status.AVAILABLE
        elif self.deleted:
            return Status.DELETED
        return Status.UNDER_OFFER
