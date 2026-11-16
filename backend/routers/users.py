"""
User Management Router for SchoolGPT
Allows Administrators and Principals to view, manage, and toggle user accounts.
RSR Technologies
"""

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User
from backend.auth.dependencies import get_current_user, require_min_role
from backend.auth.security import get_password_hash

router = APIRouter(prefix="/users", tags=["User Management"])

class UserRoleUpdate(BaseModel):
    role: str

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str
    email: Optional[str] = None

@router.get("")
def list_users(
    current_user: User = Depends(require_min_role("Principal")),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [u.to_dict() for u in users]

@router.post("")
def create_user(
    req: UserCreate,
    current_user: User = Depends(require_min_role("School Admin")),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=req.username,
        email=req.email,
        full_name=req.full_name,
        role=req.role,
        password_hash=get_password_hash(req.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.to_dict()

@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    req: UserRoleUpdate,
    current_user: User = Depends(require_min_role("School Admin")),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = req.role
    db.commit()
    return user.to_dict()

@router.put("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    req: UserStatusUpdate,
    current_user: User = Depends(require_min_role("School Admin")),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own administrator account")
    user.is_active = req.is_active
    db.commit()
    return user.to_dict()
