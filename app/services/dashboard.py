from typing import Any
from sqlmodel import Session, select, func, and_
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Aggregate revenue by month (PostgreSQL)
    stmt = (
        select(
            func.coalesce(func.date_trunc('month', Payment.payment_date), datetime.now()).label('month_start'),
            func.coalesce(func.sum(Payment.amount), 0).label('total_amount'),
        )
        .where(and_(Payment.deleted == False, Payment.status == PaymentStatus.PAID))
        .group_by(func.date_trunc('month', Payment.payment_date))
        .order_by(func.date_trunc('month', Payment.payment_date))
    )

    rows = session.exec(stmt).all()

    # Build a dict for the last 12 months, defaulting to 0
    now = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_12 = [(now - relativedelta(months=i)) for i in range(11, -1, -1)]
    # Build a list for the last 12 months, defaulting to 0
    monthly_revenue_list = [
        {"month": months[d.month - 1], "amount": 0.0} for d in last_12
    ]

    # Fill with actual sums returned from the DB
    for month_start, total in rows:
        for item in monthly_revenue_list:
            if item["month"] == months[month_start.month - 1]:
                item["amount"] = float(total or 0.0)

    return {
        "total_units": total_units,
        "total_payments": total_payments,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_outstanding": total_outstanding,
        "total_projects": total_project,
        "monthly_revenue": monthly_revenue_list
    }