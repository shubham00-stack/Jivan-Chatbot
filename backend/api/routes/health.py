from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database.connection import get_db, IS_USING_SQLITE
from backend.core.config import settings
from rag.vector_store import vector_store_manager

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_alive = False
    try:
        db.execute(text("SELECT 1"))
        db_alive = True
    except Exception:
        db_alive = False

    has_gemini_key = bool(settings.GEMINI_API_KEY)
    has_openai_key = bool(settings.OPENAI_API_KEY)

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
            "gemini_key_configured": has_gemini_key,
            "openai_key_configured": has_openai_key
        }
    }

