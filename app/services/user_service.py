from sqlmodel import Session, select
from app.models.user import User, Role
from app.core.security import hash_password, verify_password
import random
from typing import Union
from app.schemas.user import UserCreate, RegisterRequest

def create_user(session: Session, data: Union[UserCreate, RegisterRequest]):
    # Ensure fullname, email, phone are present (for RegisterRequest, may not be)
    fullname = getattr(data, "fullname", None)
    email = getattr(data, "email", None)
    phone = getattr(data, "phone", None)
    # If missing, raise error
    if not fullname or not email or not phone:
        raise ValueError("fullname, email, and phone are required.")
    code = str(random.randint(100000, 999999))
    user = User(
        fullname=fullname,
        email=email,
        phone=phone,
        hashed_password=hash_password(data.password),
        address=getattr(data, "address", None),
        role=getattr(data, "role", Role.CLIENT),
        commission_rate=getattr(data, "commission_rate", None),
        is_internal=getattr(data, "is_internal", None),
        created_by=getattr(data, "created_by", None),
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

# Retrieve all users
def get_all_users(session: Session):
    return session.exec(select(User)).all()

# Retrieve user by ID
def get_user_by_id(session: Session, user_id: str):
    return session.get(User, user_id)