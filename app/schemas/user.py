from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.unit import UnitCompletionStatus
from app.models.user import Role
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import Role
from app.schemas.company import CompanyRead

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    fullname: str
    phone: str | None = None
    created_by: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: Role
    user_id: str

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class UserBase(BaseModel):
    fullname: str
    email: str
    phone: str
    address: Optional[str] = None
    commission_rate: Optional[float] = None
    is_internal: Optional[bool] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = True
    company_id: Optional[UUID] = None
    company: Optional[CompanyRead] = None


class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    is_verified: bool
    role: Role = Role.CLIENT
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    # email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    role: Optional[Role] = None
    commission_rate: Optional[float] = None
    is_internal: Optional[bool] = None
    is_verified: Optional[bool] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = None
    reason_for_delete: Optional[str] = None

class UserList(BaseModel):
    data: list[UserRead]
    total: int

class SingleUser(UserRead):
    units: Optional[list["ClientUnit"]] = []

class ClientUnit(BaseModel):
    id: UUID
    name: str
    amount: float
    expected_initial_payment: float
    type: Optional[str] = None
    purchase_date: datetime | None = None
    installment: int = 1
    payment_plan: bool = False
    handover_date: Optional[datetime] = None
    development_status: Optional[UnitCompletionStatus] = UnitCompletionStatus.NOT_STARTED