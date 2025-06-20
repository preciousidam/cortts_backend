from sqlmodel import Session, select
from app.models.payment import Payment
from uuid import UUID

from app.schemas.paging import Paging
from app.utility.paging import paginate

def create_payment(session: Session, data):
    data_dict = data.model_dump()
    data_dict["unit_id"] = UUID(data_dict["unit_id"])  # ensure UUID type
    payment = Payment(**data_dict)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_all_payments(session: Session, paging: Paging):
    query = select(Payment).where(Payment.deleted == False)
    payments, total = paginate(session, query, paging)
    
    return {"data": payments, "total": total}

def get_payment_by_id(session: Session, payment_id: str):
    return session.get(Payment, payment_id)

def update_payment(session: Session, payment_id: str, data):
    payment = session.get(Payment, payment_id)
    if not payment or payment.deleted:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def soft_delete_payment(session: Session, payment_id: str, reason: str):
    payment = session.get(Payment, payment_id)
    if payment:
        payment.deleted = True
        payment.reason_for_delete = reason
        session.add(payment)
        session.commit()
    return payment