from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import create_user, get_all_users, get_user_by_id
from app.auth.dependencies import get_current_user
from app.models.user import Role

router = APIRouter()

@router.post("/", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def create(data: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, data)

@router.get("/", response_model=list[UserRead], dependencies=[Depends(get_current_user([Role.ADMIN]))])
def all(session: Session = Depends(get_session)):
    return get_all_users(session)

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def get(user_id: str, session: Session = Depends(get_session)):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user