"""
Authentication Router for SchoolGPT
Provides login, registration, current user, and demo accounts.
RSR Technologies
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User
from backend.auth.security import verify_password, get_password_hash, create_access_token
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "Student"
    email: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict

@router.post("/login", response_model=AuthResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == creds.username).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    user = User(
        username=req.username,
        email=req.email,
        full_name=req.full_name,
        role=req.role if req.role in ["Student", "Parent", "Teacher", "Principal", "School Admin"] else "Student",
        password_hash=get_password_hash(req.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@router.get("/demo-accounts")
def get_demo_accounts():
    """Returns demo credentials for 1-click test logins."""
    return [
        {"role": "Super Admin", "username": "admin", "password": "password123", "name": "System Administrator", "desc": "Full management access to all school systems"},
        {"role": "Principal", "username": "principal", "password": "password123", "name": "Dr. Ramesh Sharma", "desc": "Executive dashboard, confidential policies, oversight"},
        {"role": "Teacher", "username": "teacher", "password": "password123", "name": "Ms. Anita Desai", "desc": "Curriculum, exams, lesson plans & student records"},
        {"role": "Parent", "username": "parent", "password": "password123", "name": "Mr. Vikram Rao", "desc": "Fee structures, transport, circulars & leave policies"},
        {"role": "Student", "username": "student", "password": "password123", "name": "Rahul Kumar", "desc": "Syllabus, timetables, homework & club guidelines"}
    ]
