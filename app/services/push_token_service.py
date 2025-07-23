from app.models.push_token import PushToken
from uuid import UUID
from datetime import datetime, timezone
from app.models.user import User
from sqlmodel import Session, select
    

def register_push_token(session: Session, user_id: UUID, token: str, device: str = "") -> PushToken:
    # Check if already exists
    existing = session.exec(
        select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
    ).first()
    if existing:
        existing.device = device or existing.device
        existing.updated_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    push_token = PushToken(user_id=user_id, token=token, device=device)
    session.add(push_token)
    session.commit()
    session.refresh(push_token)
    return push_token

def remove_push_token(session: Session, user_id: UUID, token: str) -> bool:
    existing = session.exec(
        select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
    ).first()
    if existing:
        session.delete(existing)
        session.commit()
        return True
    return False