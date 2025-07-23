from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.services.user_service import create_user, authenticate_user, forgot_password, reset_password
from app.auth.dependencies import get_current_user
from app.schemas.user import RegisterRequest, LoginResponse, ResetPasswordRequest, VerifyRequest, ForgotPasswordRequest
from app.core.security import create_access_token
from app.models.user import User, Role

router = APIRouter()

@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    user = create_user(session, data)
    return {
        "message": "Check your email for verification code",
        "user_id": user.id,
        "verification_code": user.verification_code,
        "is_verified": user.is_verified
    }

@router.post("/verify")
def verify(data: VerifyRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or user.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    user.is_verified = True
    user.verification_code = None
    session.add(user)
    session.commit()
    token = create_access_token({"sub": user.id, "role": user.role})
    return {
        "message": "Verification successful",
        "user_id": user.id,
        "is_verified": user.is_verified,
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
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

@router.post("/refresh", response_model=LoginResponse)
def refresh_token(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = create_access_token({"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": str(user.id)
    }

@router.post("/forgot-password")
def forgot_password_route(data: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = forgot_password(session, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "Check your email for the password reset code."}

@router.post("/reset-password")
def reset_password_route(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = reset_password(session, data.email, data.code, data.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "Password reset successful."}