from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from typing import Any
from app.models.user import Role
from app.services.dashboard import get_admin_dashboard

router = APIRouter()

@router.get("/admin", response_model=dict[str, Any], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def get_admin_dashboard_route(session: Session = Depends(get_session)) -> dict[str, Any]:
    return get_admin_dashboard(session)
