from pydantic import BaseModel

class Unit(BaseModel):
    id: str
    name: str
    projectName: str
    status: str
    price: float

class DashboardSummary(BaseModel):
    total_units: int
    total_revenue: float
    total_outstanding: float
    total_projects: int
    monthly_revenue: list[dict[str, float]]
    units: list[Unit]