from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UnitBase(BaseModel):
    name: str
    amount: float
    initial_payment: float
    discount: Optional[float] = 0
    comments: Optional[str] = None
    type: Optional[str] = None
    purchase_date: datetime
    installment: int = 1
    payment_plan: bool = False
    handover_date: Optional[datetime] = None
    warranty_period: Optional[int] = 0
    client_id: Optional[str] = None
    property_id: Optional[str] = None
    agent_id: Optional[str] = None
    sales_rep: Optional[str] = None

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    initial_payment: Optional[float] = None
    discount: Optional[float] = None
    comments: Optional[str] = None
    type: Optional[str] = None
    purchase_date: Optional[datetime] = None
    installment: Optional[int] = None
    payment_plan: Optional[bool] = None
    handover_date: Optional[datetime] = None
    warranty_period: Optional[int] = None
    client_id: Optional[str] = None
    property_id: Optional[str] = None
    agent_id: Optional[str] = None
    sales_rep: Optional[str] = None

class PaymentSummary(BaseModel):
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

class UnitRead(UnitBase):
    id: str
    deleted: bool
    reason_for_delete: Optional[str]
    warranty: Optional[dict]
    payment_summary: Optional[PaymentSummary]
    graph_data: Optional[list[dict]]

    class Config:
        from_attributes = True