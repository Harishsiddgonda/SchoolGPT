"""
Bookmarks Router for SchoolGPT
Allows users to save and organize key answers and citations.
RSR Technologies
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, Bookmark
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/bookmarks", tags=["Bookmarks"])

class BookmarkCreate(BaseModel):
    query_id: Optional[int] = None
    query_text: str
    answer_text: str
    note: Optional[str] = None

@router.get("")
def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    return [b.to_dict() for b in bookmarks]

@router.post("")
def add_bookmark(
    req: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if duplicate
    existing = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id, Bookmark.query_text == req.query_text.strip())
        .first()
    )
    if existing:
        return existing.to_dict()

    bookmark = Bookmark(
        user_id=current_user.id,
        query_id=req.query_id,
        query_text=req.query_text.strip(),
        answer_text=req.answer_text.strip(),
        note=req.note
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark.to_dict()

@router.delete("/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    b = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(b)
    db.commit()
    return {"message": "Bookmark removed"}
