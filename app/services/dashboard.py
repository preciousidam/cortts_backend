from typing import Any
from sqlmodel import Session, select, func, and_

from app.models.payment import Payment
from app.models.project import Project
from app.models.unit import PaymentStatus, Unit
from app.models.user import Role, User

def get_admin_dashboard(session: Session) -> dict[str, Any]:
    total_units = session.exec(select(func.count()).select_from(Unit).where(Unit.deleted == False)).first() or 0
    total_payments = session.exec(select(func.count()).select_from(Payment).where(Payment.deleted == False)).first() or 0
    total_users = session.exec(select(func.count()).select_from(User).where(and_(User.deleted == False, User.role == Role.CLIENT))).first() or 0
    total_project = session.exec(select(func.count()).select_from(Project).where(Project.deleted == False)).first() or 0

    total_revenue = session.exec(select(func.sum(Payment.amount)).select_from(Payment).where(and_(Payment.deleted == False, Payment.status == PaymentStatus.PAID))).first() or 0
    total_outstanding = session.exec(select(func.sum(Payment.amount)).select_from(Payment).where(and_(Payment.deleted == False, Payment.status == PaymentStatus.NOT_PAID))).first() or 0

    return {
        "total_units": total_units,
        "total_payments": total_payments,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_outstanding": total_outstanding,
        "total_projects": total_project
    }