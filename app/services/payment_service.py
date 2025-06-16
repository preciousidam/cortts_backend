from sqlmodel import Session, select
from app.models.payment import Payment

def create_payment(session: Session, data):
    payment = Payment(**data.model_dump())
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_all_payments(session: Session):
    return session.exec(select(Payment).where(Payment.deleted == False)).all()

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