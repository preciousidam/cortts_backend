from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.paging import Paging
from app.services.payment_service import (
    create_payment, get_all_payments, get_payment_by_id, update_payment, soft_delete_payment
)
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentRead
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()

@router.post("/", response_model=PaymentRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: PaymentCreate, session: Session = Depends(get_session)):
    return create_payment(session, data)

@router.get("/", response_model=list[PaymentRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def all(paging: Paging = Depends(), session: Session = Depends(get_session)):
    return get_all_payments(session, paging)

@router.get("/{payment_id}", response_model=PaymentRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def get(payment_id: str, session: Session = Depends(get_session)):
    payment = get_payment_by_id(session, payment_id)
    if not payment or payment.deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.patch("/{payment_id}", response_model=PaymentRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def update(payment_id: str, data: PaymentUpdate, session: Session = Depends(get_session)):
    payment = update_payment(session, payment_id, data)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/{payment_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete(payment_id: str, reason: str, session: Session = Depends(get_session)):
    payment = soft_delete_payment(session, payment_id, reason)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted"}