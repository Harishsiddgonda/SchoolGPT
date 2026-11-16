"""
Chat & Query Router for SchoolGPT
Provides RAG query execution, conversation history, and query deletion.
RSR Technologies
"""

import json
from typing import Optional, List, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.models import User, QueryHistory
from backend.auth.dependencies import get_current_user
from backend.rag.engine import rag_engine

router = APIRouter(prefix="/api/chat", tags=["Chat & RAG"])

class ChatQueryRequest(BaseModel):
    question: str
    language: str = "en"
    conversation_history: Optional[List[Dict[str, str]]] = None

class CitationItem(BaseModel):
    doc_id: Optional[int] = None
    title: str
    category: Optional[str] = None
    page: int
    section: Optional[str] = ""
    snippet: str
    similarity: Optional[float] = 0.0

class ChatQueryResponse(BaseModel):
    answer: str
    sources: List[CitationItem]
    model: str
    response_time: float
    query_id: Optional[int] = None
    chunks_retrieved: int

@router.post("", response_model=ChatQueryResponse)
def execute_query(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = rag_engine.query(
        question=req.question,
        user_role=current_user.role,
        language=req.language,
        conversation_history=req.conversation_history
    )

    # Persist in query history
    query_record = QueryHistory(
        user_id=current_user.id,
        query_text=req.question.strip(),
        answer_text=result["answer"],
        language=req.language,
        response_time_sec=result["response_time"],
        model_used=result["model"],
        sources_json=json.dumps(result["sources"])
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "model": result["model"],
        "response_time": result["response_time"],
        "query_id": query_record.id,
        "chunks_retrieved": result["chunks_retrieved"]
    }

@router.get("/history")
def get_user_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queries = (
        db.query(QueryHistory)
        .filter(QueryHistory.user_id == current_user.id)
        .order_by(QueryHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [q.to_dict() for q in queries]

@router.delete("/history/{query_id}")
def delete_query_history(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query record not found")
    if query.user_id != current_user.id and current_user.role not in ["Super Admin", "School Admin"]:
        raise HTTPException(status_code=403, detail="Cannot delete other user's history")
    db.delete(query)
    db.commit()
    return {"message": "Query deleted successfully"}

@router.delete("/history")
def clear_all_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}
