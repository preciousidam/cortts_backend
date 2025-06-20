from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.user import User, Role
from app.core.security import hash_password, verify_password
import random
from typing import Union
from app.schemas.paging import Paging
from app.schemas.user import UserCreate, RegisterRequest, UserUpdate
from app.utility.paging import paginate

def create_user(session: Session, data: Union[UserCreate, RegisterRequest]):
    # Ensure fullname, email, phone are present (for RegisterRequest, may not be)
    fullname = getattr(data, "fullname", None)
    email = getattr(data, "email", None)
    phone = getattr(data, "phone", None)
    # If missing, raise error
    if not fullname or not email:
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
def get_all_users(session: Session, paging: Paging):
    query = select(User)
    users, total = paginate(session, query, paging)
    
    return {"data": users, "total": total}

# Retrieve user by ID
def get_user_by_id(session: Session, user_id: str):
    print(user_id)
    return session.get(User, user_id)

# Update user details
def update_user(session: Session, user_id: str, data: UserUpdate):
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
def soft_delete_user(session: Session, user_id: str, reason: str):
    user = session.get(User, user_id)
    if user:
        user.deleted = True
        user.reason_for_delete = reason
        user.deleted_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
    return user