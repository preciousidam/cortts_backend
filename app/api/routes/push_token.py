from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from app.db.session import get_session
from app.auth.dependencies import get_current_user
from app.schemas.push_token import PushTokenCreate, PushTokenRead
from app.services.push_token_service import register_push_token, remove_push_token

router = APIRouter()

@router.post("/", response_model=PushTokenRead)
def register_token(
    data: PushTokenCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    if str(current_user.id) != str(data.user_id):
        raise HTTPException(status_code=403, detail="You can only register tokens for yourself")
    return register_push_token(session, data.user_id, data.token, data.device or "")

@router.delete("/", response_model=dict)
def remove_token(
    token: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    removed = remove_push_token(session, current_user.id, token)
    if not removed:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"message": "Token removed"}