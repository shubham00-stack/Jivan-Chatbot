from fastapi import APIRouter
from backend.api.routes.health import router as health_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.documents import router as documents_router
from backend.api.routes.conversations import router as conversations_router
from backend.api.routes.feedback import router as feedback_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(documents_router)
api_router.include_router(conversations_router)
api_router.include_router(feedback_router)

