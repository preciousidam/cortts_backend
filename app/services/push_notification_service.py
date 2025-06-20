import httpx
from typing import List, Optional
from app.models.push_token import PushToken
from uuid import UUID
from datetime import datetime, timezone
from app.models.user import User
from sqlmodel import Session, select

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

class PushNotificationSender:
    @staticmethod
    async def send_push(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        image: Optional[str] = None
    ):
        messages = []
        for token in tokens:
            message = {
                "to": token,
                "sound": "default",
                "title": title,
                "body": body,
                "data": data or {},
            }
            if image:
                message["richContent"] = {"image": image}
            messages.append(message)

        async with httpx.AsyncClient() as client:
            # Expo recommends sending up to 100 notifications per request
            responses = []
            for i in range(0, len(messages), 100):
                batch = messages[i:i+100]
                resp = await client.post(EXPO_PUSH_URL, json=batch)
                responses.append(resp.json())
            return responses

    @staticmethod
    def get_tokens_for_user(session: Session, user_id):
        tokens = session.exec(
            select(PushToken.token).where(PushToken.user_id == user_id)
        ).all()
        return [t for t in tokens if t]
    

def register_push_token(session: Session, user_id: UUID, token: str, device: str = ""):
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

def remove_push_token(session: Session, user_id: UUID, token: str):
    existing = session.exec(
        select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
    ).first()
    if existing:
        session.delete(existing)
        session.commit()
        return True
    return False