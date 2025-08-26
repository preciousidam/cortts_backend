from uuid import UUID
from sqlmodel import Session, select, desc
from app.models.unit import Unit
from app.models.payment import Payment, PaymentStatus
from app.schemas.paging import Paging
from app.models.user import User, Role
from app.models.unit_agent_link import UnitAgentLink
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from app.core.config import settings
from app.utility.paging import paginate
from app.schemas.unit import PaymentDuration, UnitCreate, UnitUpdate, UnitRead
from app.schemas.unit_agent_link import UnitAgentLinkCreate, UnitAgentLinkRead

def create_unit(session: Session, data: UnitCreate) -> Unit:

    # client = session.get(User, data.client_id)
    # if not client or client.role != Role.CLIENT:
    #     raise ValueError("Provided client_id does not belong to a client")

    unit = Unit(**data.model_dump())
    session.add(unit)
    session.commit()
    session.refresh(unit)

    # Generate payments if payment_plan is enabled
    if unit.payment_plan:
        recalculate_payments(session, unit)
    else:
        payment = Payment(
            amount=unit.amount,
            due_date=unit.purchase_date,
            status=PaymentStatus.NOT_PAID,
            unit_id=unit.id
        )
        session.add(payment)
        session.commit()

    if data.agents:
        for agent in data.agents:
            session.add(UnitAgentLink(
                unit_id=unit.id,
                agent_id=agent.agent_id,
                role=agent.role
            ))
        session.commit()

    session.refresh(unit)

    return unit

def get_all_units(session: Session, paging: Paging) -> dict[str, list[UnitRead] | int]:
    query = select(Unit).where(Unit.deleted == False).order_by(desc(Unit.created_at))
    units, total = paginate(session, query, paging)

    return {"data": units, "total": total}

def get_unit_by_id(session: Session, unit_id: UUID) -> Unit | None:
    return session.get(Unit, unit_id)

def soft_delete_unit(session: Session, unit_id: UUID, reason: str) -> Unit | None:
    unit = session.get(Unit, unit_id)
    if unit:
        unit.deleted = True
        unit.reason_for_delete = reason
        session.add(unit)
        session.commit()
    return unit

def update_unit(session: Session, unit_id: UUID, data: UnitUpdate) -> Unit | None:
    unit = session.get(Unit, unit_id)
    if not unit or unit.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field != "agents":
            setattr(unit, field, value)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    # Check if any relevant payment fields were updated and payment_plan is enabled
    if any(
        field in data.model_dump(exclude_unset=True)
        for field in ["expected_initial_payment", "installment", "amount"]
    ) and unit.payment_plan:
        recalculate_payments(session, unit)

    if hasattr(data, "agents") and data.agents is not None:
        # Remove old links
        links = session.exec(select(UnitAgentLink).where(UnitAgentLink.unit_id == unit_id)).all()
        for link in links:
            session.delete(link)

        session.commit()

        # Add new links
        for agent in data.agents:
            session.add(UnitAgentLink(
                unit_id=unit.id,
                agent_id=agent.agent_id,
                role=agent.role
            ))
        session.commit()

    return unit


# Add after update_unit
def recalculate_payments(session: Session, unit: Unit)  -> None:
    # Remove existing non-deleted scheduled payments (excluding the initial payment)
    scheduled_payments = [
        p for p in unit.payments
        if p.status == PaymentStatus.NOT_PAID and not p.deleted
    ]
    for p in scheduled_payments:
        session.delete(p)
    session.commit()

    # 2) Normalize inputs
    amount = float(unit.amount or 0)
    discount_pct = float(unit.discount or 0)  # percent (e.g., 12.0 = 12%)
    initial = float(unit.expected_initial_payment or 0)
    installments = int(unit.installment or 0)
    plan_enabled = bool(unit.payment_plan)
    purchase_dt = unit.purchase_date or datetime.utcnow()

    # If plan disabled, nothing to schedule here.
    if not plan_enabled or installments <= 0:
        session.commit()
        return

    # Recalculate new monthly payments
    total = amount - (discount_pct * amount)
    remaining = total - initial
    monthly = round(remaining / installments, 2) if installments else 0

    # If initial payment was made, add it as a paid payment
    if initial > 0:
        session.add(Payment(
            amount=initial,
            due_date=purchase_dt,
            status=PaymentStatus.NOT_PAID,
            unit_id=unit.id
        ))

    for i in range(installments):
        if unit.payment_duration == PaymentDuration.MONTHLY:
            due = purchase_dt + relativedelta(months=i+1) if purchase_dt else None
            session.add(Payment(
                amount=monthly,
                due_date=due,
                status=PaymentStatus.NOT_PAID,
                unit_id=unit.id
            ))
        elif unit.payment_duration == PaymentDuration.QUARTERLY:
            due = purchase_dt + relativedelta(months=(i+1)*3) if purchase_dt else None
            session.add(Payment(
                amount=monthly,
                due_date=due,
                status=PaymentStatus.NOT_PAID,
                unit_id=unit.id
            ))
        elif unit.payment_duration == PaymentDuration.BI_ANNUALLY:
            due = purchase_dt + relativedelta(months=(i+1)*6) if purchase_dt else None
            session.add(Payment(
                amount=monthly,
                due_date=due,
                status=PaymentStatus.NOT_PAID,
                unit_id=unit.id
            ))
        elif unit.payment_duration == PaymentDuration.ANNUALLY:
            due = unit.purchase_date + relativedelta(years=i+1) if unit.purchase_date else None
            session.add(Payment(
                amount=monthly,
                due_date=due,
                status=PaymentStatus.NOT_PAID,
                unit_id=unit.id
            ))

    session.commit()

def warranty_info(unit: Unit)  -> dict[str, bool | str] | None:
    return unit.warranty

def payment_summary(unit: Unit)  -> dict[str, float | int | str | None]:
    return unit.payment_summary

def graph_data(unit: Unit) -> list[dict[str, float | int]]:
    # summary = payment_summary(unit)
    return unit.graph_data