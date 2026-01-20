from decimal import Decimal
import uuid
from pydantic import BaseModel
from app.schemas.payment import PaymentStatus

class Unit(BaseModel):
    id: uuid.UUID
    name: str
    projectName: str
    status: str
    price: Decimal
    image: str | None

class Payment(BaseModel):
    id: uuid.UUID
    amount: Decimal
    payment_date: str
    status: PaymentStatus
    reason_for_payment: str | None
    title: str | None

class MonthlyRevenueItem(BaseModel):
    month: str
    amount: float

class DashboardSummary(BaseModel):
    total_units: int
    total_revenue: Decimal
    total_outstanding: Decimal
    total_projects: int
    total_users: int
    total_payments: int
    monthly_revenue: list[MonthlyRevenueItem]
    units: list[Unit]
    recent_payments: list[Payment]  # You can define a specific schema for payments if needed