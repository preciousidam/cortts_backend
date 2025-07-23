from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import EmailStr
from sqlmodel import Session, select, or_
from app.models.user import User, Role
from app.core.security import hash_password, verify_password
import random
from typing import Union
from app.schemas.paging import Paging
from app.schemas.user import UserCreate, RegisterRequest, UserUpdate
from app.utility.paging import paginate


def create_user(session: Session, data: Union[UserCreate, RegisterRequest]) -> User:
    # Ensure fullname, email, phone are present (for RegisterRequest, may not be)
    fullname = getattr(data, "fullname", None)
    email = getattr(data, "email", None)
    phone = getattr(data, "phone", None)

    # If missing, raise error
    if not fullname or not email or not phone:
        raise HTTPException(status_code=400, detail="fullname, email, and phone are required.")

    user = session.exec(select(User).where(or_(User.email == email, User.phone == phone))).first()

    if user:
        raise HTTPException(status_code=409, detail="Email or phone number already registered.")

    # Generate a 6-digit verification code
    code = str(random.randint(100000, 999999))
    user = User(
        fullname=fullname,
        email=email,
        phone=phone,
        hashed_password=hash_password(data.password),
        address=getattr(data, "address", None),
        role=Role.CLIENT,
        commission_rate=getattr(data, "commission_rate", None),
        is_internal=getattr(data, "is_internal", None),
        created_by=getattr(data, "created_by", None),
        verification_code=code,
        is_verified=False,
        company_id= getattr(data, "company_id", None)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    print(f"[DEBUG] Verification code for {user.email}: {code}")
    return user

def authenticate_user(session: Session, email: str, password: str)  -> User | None:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified.")
    return user

# Retrieve all users
def get_all_users(session: Session, paging: Paging) -> dict[str, Union[list[User], int]]:
    query = select(User)
    users, total = paginate(session, query, paging)

    return {"data": users, "total": total}

# Retrieve user by ID
def get_user_by_id(session: Session, user_id: str)  -> User | None:
    return session.get(User, user_id)

# Update user details
def update_user(session: Session, user_id: str, data: UserUpdate) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Soft delete user
def soft_delete_user(session: Session, user_id: str, reason: str) -> User | None:
    user = session.get(User, user_id)
    if user:
        user.deleted = True
        user.reason_for_delete = reason
        user.deleted_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
    return user

def forgot_password(session: Session, email: EmailStr) -> User | None:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Generate a new verification code for password reset
    code = str(random.randint(100000, 999999))
    user.verification_code = code
    session.add(user)
    session.commit()

    print(f"[DEBUG] Password reset code for {user.email}: {code}")
    return user

def reset_password(session: Session, email: EmailStr, code: str, new_password: str) -> User | None:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    user.hashed_password = hash_password(new_password)
    user.verification_code = None  # Clear the code after successful reset
    session.add(user)
    session.commit()
    session.refresh(user)
    return user