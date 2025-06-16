from sqlmodel import Session, select
from app.models.user import User
from app.core.security import hash_password, verify_password
import random

def create_user(session: Session, email: str, password: str, role, created_by=None):
    code = str(random.randint(100000, 999999))
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
        created_by=created_by,
        verification_code=code,
        is_verified=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    print(f"[DEBUG] Verification code for {user.email}: {code}")
    return user

def authenticate_user(session: Session, email: str, password: str):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password) or not user.is_verified:
        return None
    return user