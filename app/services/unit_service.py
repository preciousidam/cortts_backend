from sqlmodel import Session, select
from app.models.unit import Unit
from app.models.payment import Payment, PaymentStatus
from datetime import date
from dateutil.relativedelta import relativedelta
import math

def create_unit(session: Session, data):
    from app.models.user import User, Role

    client = session.get(User, data.client_id)
    if not client or client.role != Role.CLIENT:
        raise ValueError("Provided client_id does not belong to a client")

    unit = Unit(**data.model_dump())
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit

def get_all_units(session: Session):
    return session.exec(select(Unit).where(Unit.deleted == False)).all()

def get_unit_by_id(session: Session, unit_id: str):
    return session.get(Unit, unit_id)

def soft_delete_unit(session: Session, unit_id: str, reason: str):
    unit = session.get(Unit, unit_id)
    if unit:
        unit.deleted = True
        unit.reason_for_delete = reason
        session.add(unit)
        session.commit()
    return unit

def update_unit(session: Session, unit_id: str, data):
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit

def warranty_info(unit: Unit):
    if not unit.handover_date or not unit.warranty_period:
        return {"isValid": False, "expire_at": None}
    expire_at = unit.handover_date + relativedelta(months=+unit.warranty_period)
    return {"isValid": date.today() <= expire_at, "expire_at": expire_at}

def payment_summary(unit: Unit):
    total_deposit = unit.initial_payment
    total_unpaid = 0
    total_sch = 0

    for p in unit.payments:
        total_sch += p.amount
        if p.status == PaymentStatus.paid:
            total_deposit += p.amount
        else:
            total_unpaid += p.amount

    installment_amount = unit.amount - unit.initial_payment
    outstanding = unit.amount - total_deposit
    balanced = installment_amount == total_sch
    more_or_less = "less" if installment_amount > total_sch else "more"
    percentage_paid = (total_deposit / unit.amount) * 100
    percentage_unpaid = (total_unpaid / unit.amount) * 100
    diff = abs(installment_amount - total_sch)

    return {
        "outstanding": outstanding,
        "total_deposit": total_deposit,
        "total_unpaid": total_unpaid,
        "balanced": balanced,
        "more_or_less": more_or_less,
        "percentage_paid": percentage_paid,
        "percentage_unpaid": percentage_unpaid,
        "installment_amount": installment_amount,
        "total_sch": total_sch,
        "installment_diff": diff
    }

def graph_data(unit: Unit):
    summary = payment_summary(unit)
    return {
        "labels": ["paid", "unpaid"],
        "data": [summary["total_deposit"], summary["installment_amount"]]
    }