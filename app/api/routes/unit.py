from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.services.unit_service import (
    create_unit, get_all_units, get_unit_by_id, update_unit,
    soft_delete_unit, warranty_info, payment_summary, graph_data
)
from app.schemas.unit import UnitCreate, UnitUpdate, UnitRead

router = APIRouter()

@router.post("/", response_model=UnitRead)
def create(data: UnitCreate, session: Session = Depends(get_session)):
    return create_unit(session, data)

@router.get("/", response_model=list[UnitRead])
def all_units(session: Session = Depends(get_session)):
    return get_all_units(session)

@router.get("/{unit_id}", response_model=UnitRead)
def get(unit_id: str, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit or unit.deleted:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.patch("/{unit_id}", response_model=UnitRead)
def update(unit_id: str, data: UnitUpdate, session: Session = Depends(get_session)):
    unit = update_unit(session, unit_id, data)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.delete("/{unit_id}")
def delete(unit_id: str, reason: str, session: Session = Depends(get_session)):
    unit = soft_delete_unit(session, unit_id, reason)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Unit deleted"}

@router.get("/{unit_id}/warranty")
def get_warranty(unit_id: str, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return warranty_info(unit)

@router.get("/{unit_id}/payment-summary")
def get_payment_summary(unit_id: str, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return payment_summary(unit)

@router.get("/{unit_id}/graph-data")
def get_graph_data(unit_id: str, session: Session = Depends(get_session)):
    unit = get_unit_by_id(session, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return graph_data(unit)