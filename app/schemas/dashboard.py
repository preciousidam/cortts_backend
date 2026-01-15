from pydantic import BaseModel

class Unit(BaseModel):
    id: str
    name: str
    projectName: str
    status: str
    price: float
    image: str | None

class MonthlyRevenueItem(BaseModel):
    month: str
    amount: float

class DashboardSummary(BaseModel):
    total_units: int
    total_revenue: float
    total_outstanding: float
    total_projects: int
    total_users: int
    total_payments: int
    monthly_revenue: list[MonthlyRevenueItem]
    units: list[Unit]