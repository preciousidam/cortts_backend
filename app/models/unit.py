from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from enum import Enum
from app.models.timestamp_mixin import TimestampMixin

class PaymentStatus(str, Enum):
    PAID = "paid"
    NOT_PAID = "not_paid"
    OVERDUE = "overdue"


class Unit(SQLModel, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    amount: float
    expected_initial_payment: float
    discount: float = 0.0
    comments: Optional[str] = None
    type: Optional[str] = None
    purchase_date: datetime
    installment: int = 1
    payment_plan: bool = False
    client_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    project_id: Optional[UUID] = Field(default=None, foreign_key="project.id")
    handover_date: Optional[datetime] = None
    deleted: bool = False
    reason_for_delete: Optional[str] = None

    unit_agents: List["UnitAgentLink"] = Relationship(back_populates="unit")
    client: Optional["User"] = Relationship(back_populates="units")
    project: Optional["Project"] = Relationship(back_populates="units")
    payments: List["Payment"] = Relationship(back_populates="unit")

    @property
    def warranty(self) -> Optional[str]:
        if not self.handover_date:
            return None
        warranty_end = self.handover_date + timedelta(days=365)
        return warranty_end.strftime("%Y-%m-%d")

    @property
    def payment_summary(self) -> Dict[str, Any]:
        total = self.amount - self.discount
        total_deposit = self.total_paid
        outstanding = total - total_deposit
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
        }

    @property
    def graph_data(self) -> List[Dict[str, Any]]:
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
    def total_paid(self):
        return sum(p.amount for p in self.payments if p.status == PaymentStatus.PAID)