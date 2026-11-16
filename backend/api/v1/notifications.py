"""
Notifications Router for SchoolGPT API v1
RSR Technologies
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import User, Notification
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    if not notifs:
        # Generate default welcome notification
        return [
            {
                "id": 1,
                "user_id": current_user.id,
                "title": f"Welcome to SchoolGPT, {current_user.full_name}!",
                "message": f"You are logged in as {current_user.role}. You can query all institutional documents authorized for your role.",
                "type": "info",
                "is_read": False,
                "created_at": None
            }
        ]
    return [n.to_dict() for n in notifs]

@router.put("/{notif_id}/read")
def mark_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Notification marked as read"}
