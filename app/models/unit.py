from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta, timezone, date
from uuid import UUID, uuid4
from enum import Enum

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
    amount: float
    expected_initial_payment: float
    discount: float = 0.0
    comments: Optional[str] = None
    type: Optional[PropertyType] = None
    purchase_date: datetime | None = None
    installment: int = 1
    payment_plan: bool = False
    client_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    project_id: Optional[UUID] = Field(default=None, foreign_key="project.id")
    media_files: List["MediaFile"] = Relationship(back_populates="unit")
    handover_date: Optional[datetime] = None
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
        total = self.amount - (self.amount * self.discount / 100)
        total_deposit = self.total_paid
        outstanding = total - total_deposit - self.expected_initial_payment
        total_sch = self.installment
        installment_amount = round(max(outstanding, 0) / total_sch, 2)

        percentage_paid = round((total_deposit / total) * 100, 2) if total else 0
        percentage_unpaid = max(0, 100 - percentage_paid)
        balanced = outstanding <= 0
        more_or_less = "equal"
        installment_diff = 0.0

        if outstanding < 0:
            more_or_less = "overpaid"
            installment_diff = abs(outstanding)
        elif outstanding > 0:
            more_or_less = "underpaid"
            installment_diff = outstanding

        return {
            "total": round(total, 2),
            "outstanding": round(outstanding, 2),
            "total_deposit": round(total_deposit, 2),
            "total_unpaid": round(total - total_deposit, 2),
            "balanced": balanced,
            "more_or_less": more_or_less,
            "percentage_paid": percentage_paid,
            "percentage_unpaid": percentage_unpaid,
            "installment_amount": installment_amount,
            "total_sch": total_sch,
            "installment_diff": round(installment_diff, 2),
            "duration": self.payment_duration.value if self.payment_duration else None
        }

    @property
    def graph_data(self) -> List[Dict[str, float | int]]:
        if not self.installment:
            return []
        total = self.amount - self.discount
        balance = total - self.expected_initial_payment
        monthly_payment = balance / self.installment
        return [
            {"month": i + 1, "amount": round(monthly_payment, 2)}
            for i in range(self.installment)
        ]

    @property
    def total_paid(self) -> float:
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