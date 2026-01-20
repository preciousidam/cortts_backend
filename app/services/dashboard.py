from typing import Any
from decimal import Decimal
from sqlmodel import Session, select , and_, desc, not_
from sqlalchemy import DateTime, cast, func
from datetime import datetime,timezone
from dateutil.relativedelta import relativedelta
from app.models.payment import Payment, PaymentStatus
from app.models.project import Project
from app.models.unit import Unit
from app.models.user import Role, User
from app.schemas.dashboard import DashboardSummary, MonthlyRevenueItem, Unit as UnitSchema, Payment as PaymentSchema
from app.schemas.payment import PaymentStatus as PaymentStatusSchema

def get_admin_dashboard(session: Session) -> DashboardSummary:
    total_units = session.exec(select(func.count()).select_from(Unit).where(Unit.deleted == False)).one() or 0
    total_payments = session.exec(select(func.count()).select_from(Payment).where(Payment.deleted == False)).one() or 0
    total_users = session.exec(select(func.count()).select_from(User).where(and_(User.deleted == False, User.role == Role.CLIENT))).one() or 0
    total_projects = session.exec(select(func.count()).select_from(Project).where(Project.deleted == False)).one() or 0

    total_revenue_result = session.exec(select(func.sum(Payment.amount)).select_from(Payment).where(and_(Payment.deleted == False, Payment.status == PaymentStatus.PAID))).first()
    total_revenue = total_revenue_result if total_revenue_result is not None else Decimal("0")
    total_outstanding_result = session.exec(select(func.sum(Payment.amount)).select_from(Payment).where(and_(Payment.deleted == False, Payment.status == PaymentStatus.NOT_PAID))).first()
    total_outstanding = total_outstanding_result if total_outstanding_result is not None else Decimal("0")

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
            id=unit.id,
            name=unit.name,
            projectName=unit.project.name if unit.project else "",
            status=unit.status.value,
            price=float(unit.amount),
            image=unit.images[0] if unit.images else None,
        )
        for unit in first_20_units
    ]

    cutoff = datetime.now(timezone.utc) - relativedelta(days=30)
    payment_date_column = Payment.payment_date

    recent_payments = list(
        session.exec(
            select(Payment)
            .where(
                and_(
                    not_(Payment.deleted),
                    Payment.status == PaymentStatus.PAID,
                    payment_date_column.is_not(None),
                    payment_date_column >= cutoff,
                )
            )
            .order_by(desc(Payment.payment_date))
            .limit(5)
        ).all()
    )

    recent_payments_schema: list[PaymentSchema] = [
        PaymentSchema(
            id=payment.id,
            amount=float(payment.amount),
            payment_date=payment.payment_date.isoformat() if payment.payment_date else "",
            status=PaymentStatusSchema(payment.status.value),
            reason_for_payment=payment.reason_for_payment,
            title=payment.unit.name if payment.unit else None,
        )
        for payment in recent_payments
    ]

    return DashboardSummary(
        total_units=total_units,
        total_payments=total_payments,
        total_users=total_users,
        total_revenue=float(total_revenue),
        total_outstanding=float(total_outstanding),
        total_projects=total_projects,
        monthly_revenue=monthly_revenue_list,
        units=unit_previews,
        recent_payments=recent_payments_schema,
    )