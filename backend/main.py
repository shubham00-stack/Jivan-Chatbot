from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logging import logger
from backend.database.connection import init_db
from backend.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Vector store
    logger.info("Starting up Multimodal AI Chatbot backend...")
    init_db()
    logger.info("Application startup completed successfully.")
    yield
    # Shutdown
    logger.info("Shutting down Multimodal AI Chatbot backend...")

app = FastAPI(
    title="Multimodal AI Chatbot with RAG & Emotional Support",
    description="Production-grade MVP backend providing multimodal interaction, RAG knowledge grounding, personal emotional support, and security guardrails.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from Streamlit UI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Safe Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again or contact system support.",
            "type": exc.__class__.__name__
        }
    )

# Include API Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)

