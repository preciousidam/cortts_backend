from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.services.unit_service import (
    create_unit, get_all_units, get_unit_by_id, update_unit,
    soft_delete_unit, warranty_info, payment_summary, graph_data
)
from app.schemas.unit import UnitCreate, UnitUpdate, UnitRead, PaymentSummary, GraphDataPoint, ReadAllUnits
from app.schemas.paging import Paging
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()

@router.post("/", response_model=UnitRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: UnitCreate, session: Session = Depends(get_session)):
    return create_unit(session, data)

@router.get("/", response_model=ReadAllUnits, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def all_units(paging: Paging = Depends(), session: Session = Depends(get_session)):
    return get_all_units(session, paging)

@router.get("/{unit_id}", response_model=UnitRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def get(unit_id: UUID, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit or unit.deleted:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.patch("/{unit_id}", response_model=UnitRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def update(unit_id: UUID, data: UnitUpdate, session: Session = Depends(get_session)):
    unit = update_unit(session, unit_id, data)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.delete("/{unit_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete(unit_id: UUID, reason: str, session: Session = Depends(get_session)):
    unit = soft_delete_unit(session, unit_id, reason)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Unit deleted"}

@router.get("/{unit_id}/warranty", dependencies=[Depends(get_current_user([Role.ADMIN, Role.AGENT, Role.CLIENT]))])
def get_warranty(unit_id: UUID, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return warranty_info(unit)

@router.get("/{unit_id}/payment-summary", response_model=PaymentSummary, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT]))])
def get_payment_summary(unit_id: UUID, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return payment_summary(unit)

@router.get("/{unit_id}/graph-data", response_model=list[GraphDataPoint], dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT]))])
def get_graph_data(unit_id: UUID, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return graph_data(unit)