"""
Authentication & Authorization Dependencies
RSR Technologies
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User
from backend.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

ROLE_HIERARCHY = {
    "Super Admin": 100,
    "School Admin": 90,
    "Admin": 90,
    "Principal": 80,
    "Teacher": 60,
    "Parent": 40,
    "Student": 20
}

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        # Check for demo/dev authorization fallback or raise
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return user

def require_min_role(min_role: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_weight = ROLE_HIERARCHY.get(current_user.role, 0)
        required_weight = ROLE_HIERARCHY.get(min_role, 0)
        if user_weight < required_weight:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires at least {min_role} role."
            )
        return current_user
    return role_checker

def require_any_role(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role not in ["Super Admin", "School Admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
