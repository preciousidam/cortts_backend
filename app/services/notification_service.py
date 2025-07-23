from sqlmodel import Session, select, desc
import asyncio
from app.models.notification import Notification
from app.schemas.paging import Paging
from app.schemas.notification import NotificationCreate, NotificationRead
from app.utility.paging import paginate
from datetime import datetime, timezone
from uuid import UUID
from .push_notification_service import PushNotificationSender


def create_notification(session: Session, data: NotificationCreate) -> Notification:
    notification = Notification(**data.model_dump())
    session.add(notification)
    session.commit()
    session.refresh(notification)
    # Send push notification if the user has tokens
    tokens = PushNotificationSender.get_tokens_for_user(session, notification.user_id)
    if tokens:
        # Use asyncio.create_task if called inside an async FastAPI context,
        # or asyncio.run if outside (be careful with event loops!)
        asyncio.create_task(
            PushNotificationSender.send_push(
                tokens=tokens,
                title=notification.title,
                body=notification.body,
                data=notification.data,
            )
        )
    return notification

def get_notifications_for_user(session: Session, user_id: UUID, paging: Paging) -> dict[str, list[Notification] | int]:
    query = select(Notification).where(Notification.user_id == user_id).order_by(desc(Notification.created_at))
    notifications, total = paginate(session, query, paging)
    return {"data": notifications, "total": total}

def mark_notification_read(session: Session, notification_id: UUID) -> Notification | None:
    notification = session.get(Notification, notification_id)
    if notification:
        notification.read = True
        notification.updated_at = datetime.now(timezone.utc)
        session.add(notification)
        session.commit()
        session.refresh(notification)
    return notification

def delete_notification(session: Session, notification_id: UUID) -> Notification | None:
    notification = session.get(Notification, notification_id)
    if notification:
        session.delete(notification)
        session.commit()
    return notification

def get_notification_by_id(session: Session, notification_id: UUID) -> Notification | None:
    return session.get(Notification, notification_id)

def batch_mark_notifications_read(session: Session, user_id: UUID, notification_ids: list[UUID]) -> int:
    # Mark all provided notifications as read, must belong to user
    notifications = session.exec(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.id.in_(notification_ids)
        )
    ).all()
    now = datetime.now(timezone.utc)
    for n in notifications:
        n.read = True
        n.updated_at = now
        session.add(n)
    session.commit()
    return len(notifications)

def get_all_notifications_admin(session: Session, paging: Paging) -> dict[str, list[Notification] | int]:
    # Admin gets paginated notifications across all users
    query = select(Notification).order_by(desc(Notification.created_at))
    notifications, total = paginate(session, query, paging)
    return {"data": notifications, "total": total}