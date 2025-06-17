from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import Role
from app.services.user_service import get_user_by_id
from sqlmodel import Session
from app.db.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(required_roles: list[Role] | None = None):
    def dependency(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            role: str = payload.get("role")
            if user_id is None or role is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = get_user_by_id(session, user_id)
        if user is None:
            raise credentials_exception

        if required_roles and Role(role) not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )
        return user
    return dependency