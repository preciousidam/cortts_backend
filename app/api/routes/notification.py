from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlmodel import Session, select
from app.db.session import get_session
from app.auth.dependencies import get_current_user
from app.schemas.notification import NotificationRead, NotificationList
from app.schemas.paging import Paging
from app.services.notification_service import get_notifications_for_user, get_all_notifications_admin, get_notification_by_id, delete_notification, batch_mark_notifications_read  # Import the missing function
from app.models.user import Role
from app.utility.paging import paginate

router = APIRouter()

# List notifications for current user (with paging)
@router.get("/me", response_model=NotificationList, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def list_notifications(
    paging: Paging = Depends(),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    user = current_user
    return get_notifications_for_user(session, user.id, paging)

# Admin: List notifications for any user
@router.get("/admin/{user_id}", response_model=NotificationList, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def list_notifications_admin(
    user_id: UUID,
    paging: Paging = Depends(),
    session: Session = Depends(get_session)
):
    return get_notifications_for_user(session, user_id, paging)

# Batch mark as read
@router.post("/mark-as-read", response_model=dict, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def batch_mark_as_read(
    notification_ids: List[UUID],
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    if not notification_ids:
        raise HTTPException(status_code=400, detail="No notification IDs provided")
    updated_count = batch_mark_notifications_read(session, current_user.id, notification_ids)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="No notifications found for the provided IDs")
    return {"updated": updated_count}

# Get notification by ID
@router.get("/{notification_id}", response_model=NotificationRead, dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def get_notification(
    notification_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    notification = get_notification_by_id(session, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this notification")
    return notification

# Delete notification
@router.delete("/{notification_id}", dependencies=[Depends(get_current_user([Role.ADMIN, Role.CLIENT, Role.AGENT]))])
def delete_notification_route(
    notification_id: UUID,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    notification = delete_notification(session, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this notification")
    return {"message": "Notification deleted successfully"}

# Admin: Get all notifications across all users
@router.get("/admin", response_model=NotificationList, dependencies=[Depends(get_current_user([Role.ADMIN]))])
def get_all_notifications_admin_route(
    paging: Paging = Depends(),
    session: Session = Depends(get_session)
):
    return get_all_notifications_admin(session, paging)