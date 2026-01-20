from typing import Any
from sqlmodel import Session, select, func, and_
from sqlalchemy import DateTime, cast
from datetime import datetime,timezone
from dateutil.relativedelta import relativedelta
from app.models.payment import Payment, PaymentStatus
from app.models.project import Project
from app.models.unit import Unit
from app.models.user import Role, User
from app.schemas.dashboard import DashboardSummary, MonthlyRevenueItem, Unit as UnitSchema

def get_admin_dashboard(session: Session) -> DashboardSummary:
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
    now = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_12 = [(now - relativedelta(months=i)) for i in range(11, -1, -1)]
    # Build a list for the last 12 months, defaulting to 0
    monthly_revenue_list = [
        MonthlyRevenueItem(month=months[d.month - 1], amount=0.0) for d in last_12
    ]

    # Fill with actual sums returned from the DB
    for month_start, total in rows:
        for item in monthly_revenue_list:
            if item.month == months[month_start.month - 1]:
                item.amount = float(total or 0.0)

    # Return first 20 units
    first_20_units = session.exec(select(Unit).where(Unit.deleted == False).limit(20)).all()

    # format units to match schema
    unit_previews: list[UnitSchema] = [
        UnitSchema(
            id=str(unit.id),
            name=unit.name,
            projectName=unit.project.name if unit.project else "",
            status=unit.status.value,
            price=unit.amount,
            image=unit.images[0] if unit.images else None,
        )
        for unit in first_20_units
    ]

    cutoff = datetime.now(timezone.utc) - relativedelta(days=30)

    recent_payments = session.exec(
        select(Payment)
        .where(
            and_(
                not Payment.deleted,
                Payment.status == PaymentStatus.PAID,
                cast(Payment.payment_date, DateTime(timezone=True)).is_not(None),
                cast(Payment.payment_date, DateTime(timezone=True)) > cutoff,
            )
        )
        .order_by(Payment.payment_date.desc())
        .limit(5)
    ).all()

    return DashboardSummary(
        total_units=total_units,
        total_payments=total_payments,
        total_users=total_users,
        total_revenue=total_revenue,
        total_outstanding=total_outstanding,
        total_projects=total_project,
        monthly_revenue=monthly_revenue_list,
        units=unit_previews,
        recent_payments=recent_payments,
    )