from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.paging import Paging
from app.schemas.unit import UnitCreate
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate
from app.services.user_service import create_user, get_all_users, get_user_by_id, soft_delete_user, update_user
from app.auth.dependencies import get_current_user
from app.models.user import Role, User

router = APIRouter()

@router.post("/", response_model=UnitCreate, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, data)

@router.get("/", response_model=UserList, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def all(paging: Paging = Depends(), session: Session = Depends(get_session), role: Role | None = None, q: str | None = None):
    filter = {}
    if role:
        filter["role"] = role
    return get_all_users(session, paging, filter, q)

@router.get("/me", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def get_me(current_user: User = Depends(get_current_user())):
    return current_user

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def get(user_id: str, session: Session = Depends(get_session)):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/me", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def update_me(data: UserUpdate, current_user=Depends(get_current_user()), session: Session = Depends(get_session)):
    user = update_user(session, current_user.id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def update(user_id: str, data: UserUpdate, session: Session = Depends(get_session)):
    return update_user(session, user_id, data)

@router.delete("/{user_id}", dependencies=[Depends(get_current_user([Role.ADMIN]))])
def delete(user_id: str, reason: str, session: Session = Depends(get_session)):
    return soft_delete_user(session, user_id, reason)