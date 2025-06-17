from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.services.user_service import create_user, authenticate_user
from app.schemas.user import RegisterRequest, LoginResponse
from app.core.security import create_access_token
from app.models.user import User, Role

router = APIRouter()

@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    role = data.role if data.role is not None else Role.CLIENT
    user = create_user(session, data)
    return {
        "message": "Check your email for verification code",
        "user_id": user.id,
        "verification_code": user.verification_code,
        "is_verified": user.is_verified
    }

@router.post("/verify")
def verify(email: str, code: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or user.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    user.is_verified = True
    user.verification_code = None
    session.add(user)
    session.commit()
    return {
        "message": "Verification successful",
        "user_id": user.id,
        "is_verified": user.is_verified
    }

@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials or unverified email")
    token = create_access_token({"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": str(user.id)
    }