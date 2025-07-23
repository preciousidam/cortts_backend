from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from uuid import UUID
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if "sub" in to_encode and isinstance(to_encode["sub"], UUID):
        to_encode["sub"] = str(to_encode["sub"])
    if "role" in to_encode and isinstance(to_encode["role"], Enum):
        to_encode["role"] = to_encode["role"].value
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES if isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int) else 0
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire})
    if not settings.SECRET_KEY or not isinstance(settings.SECRET_KEY, str):
        raise ValueError("SECRET_KEY must be a non-empty string.")
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)