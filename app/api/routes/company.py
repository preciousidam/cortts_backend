from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.company import CompanyCreate, CompanyRead
from app.services.company_service import (
    create_company, get_all_companies, get_company_by_id, update_company, soft_delete_company
)
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()

@router.post("/", response_model=CompanyRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: CompanyCreate, session: Session = Depends(get_session)):
    return create_company(session, data)

@router.get("/", response_model=list[CompanyRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def all(session: Session = Depends(get_session)):
    return get_all_companies(session)

@router.get("/{company_id}", response_model=CompanyRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def get(company_id: str, session: Session = Depends(get_session)):
    company = get_company_by_id(session, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.patch("/{company_id}", response_model=CompanyRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def update(company_id: str, data: CompanyCreate, session: Session = Depends(get_session)):
    return update_company(session, company_id, data)

@router.delete("/{company_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete(company_id: str, reason: str, session: Session = Depends(get_session)):
    return soft_delete_company(session, company_id, reason)