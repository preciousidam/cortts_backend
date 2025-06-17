from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import Role
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import Role

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    fullname: str
    phone: str | None = None
    role: Optional[Role] = Role.CLIENT
    created_by: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: Role
    user_id: str


class UserBase(BaseModel):
    fullname: str
    email: str
    phone: str
    address: Optional[str] = None
    role: Role = Role.CLIENT
    commission_rate: Optional[float] = None
    is_internal: Optional[bool] = None
    created_by: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime