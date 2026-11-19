from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional

from backend.database.connection import get_db, IS_USING_SQLITE
from backend.core.config import settings
from backend.services.llm_service import llm_service
from rag.vector_store import vector_store_manager

router = APIRouter(tags=["Health & Config"])

class KeyConfigRequest(BaseModel):
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    provider: Optional[str] = None

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_alive = False
    try:
        db.execute(text("SELECT 1"))
        db_alive = True
    except Exception:
        db_alive = False

    has_groq_key = bool(settings.GROQ_API_KEY)
    has_gemini_key = bool(settings.GEMINI_API_KEY)
    has_anthropic_key = bool(settings.ANTHROPIC_API_KEY)

    return {
        "status": "healthy",
        "database": {
            "connected": db_alive,
            "engine": "sqlite" if IS_USING_SQLITE else "mysql",
        },
        "vector_store": {
            "ready": True,
            "total_chunks": vector_store_manager.get_total_chunks()
        },
        "ai_provider": {
            "active_provider": settings.LLM_PROVIDER,
            "groq_configured": has_groq_key,
            "gemini_configured": has_gemini_key,
            "anthropic_configured": has_anthropic_key
        }
    }

@router.post("/config/keys")
def update_api_keys(req: KeyConfigRequest):
    status_info = llm_service.reload_keys(
        groq_key=req.groq_api_key,
        gemini_key=req.gemini_api_key,
        anthropic_key=req.anthropic_api_key,
        provider=req.provider
    )
    return {"success": True, "status": status_info}
