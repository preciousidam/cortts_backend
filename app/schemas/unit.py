from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.unit_agent_link import AgentRole
from app.models.unit import UnitCompletionStatus, Status
from app.schemas.payment import PaymentRead

class PaymentDuration(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BI_ANNUALLY = "bi_annually"
    ANNUALLY = "annually"
class AgentAssignment(BaseModel):
    agent_id: UUID
    role: AgentRole

class UnitBase(BaseModel):
    name: str
    amount: float
    expected_initial_payment: float
    discount: Optional[float] = 0
    comments: Optional[str] = None
    type: Optional[str] = None
    purchase_date: datetime | None = None
    installment: int = 1
    payment_plan: bool = False
    handover_date: Optional[datetime] = None
    warranty_period: Optional[int] = 0
    client_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    # agent_id: Optional[UUID] = None
    sales_rep: Optional[str] = None
    development_status: Optional[UnitCompletionStatus] = UnitCompletionStatus.NOT_STARTED
    payment_duration: Optional[str] = None  # e.g., "MONTHLY", "QUARTERLY", etc.

class UnitCreate(UnitBase):
    agents: list[AgentAssignment] | None = []

class UnitUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    expected_initial_payment: Optional[float] = None
    discount: Optional[float] = None
    comments: Optional[str] = None
    type: Optional[str] = None
    purchase_date: Optional[datetime] = None
    installment: Optional[int] = None
    payment_plan: Optional[bool] = None
    payment_duration: Optional[str] = None
    handover_date: Optional[datetime] = None
    warranty_period: Optional[int] = None
    client_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    handover_date: Optional[datetime] = None
    warranty_period: Optional[int] = None
    client_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    # agent_id: Optional[UUID] = None
    sales_rep: Optional[UUID] = None
    agents: list[AgentAssignment] | None = None
    development_status: Optional[UnitCompletionStatus] = None
    deleted: bool | None = None
    reason_for_delete: Optional[str] = None

class PaymentSummary(BaseModel):
    total: float
    outstanding: float
    total_deposit: float
    total_unpaid: float
    balanced: bool
    more_or_less: str
    percentage_paid: float
    percentage_unpaid: float
    installment_amount: float
    total_sch: float
    installment_diff: float
    duration: Optional[str] = None  # e.g., "MONTHLY", "QUARTERLY", etc.

class GraphDataPoint(BaseModel):
    month: int
    amount: float
class WarrantyInfo(BaseModel):
    isValid: bool = False
    expire_at: Optional[str] = None

class UserRead(BaseModel):
    id: UUID
    fullname: str
    email: str
    phone: str | None = None
    is_verified: bool

class UnitRead(UnitBase):
    id: UUID
    deleted: bool
    reason_for_delete: Optional[str]
    warranty: Optional[WarrantyInfo]
    payment_summary: Optional[PaymentSummary]
    graph_data: Optional[list[GraphDataPoint]]
    images: Optional[List[str]] = []  # Assuming images are stored as URLs or file paths
    total_paid: float = 0
    client: Optional[UserRead] = None
    status: Status
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class Agent(BaseModel):
    agent: UserRead
    role: AgentRole

class SingleUnit(UnitRead):
    unit_agents: List[Agent] = []

class ReadAllUnits(BaseModel):
    data: List[UnitRead]
    total: int

class UnitPayments(BaseModel):
    data: list[PaymentRead]
    total: int