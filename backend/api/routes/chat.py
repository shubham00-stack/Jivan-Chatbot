import json
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.core.security import rate_limiter
from backend.schemas.chat_schema import ChatRequest, ChatResponse
from backend.services.chat_service import chat_service
from backend.services.multimodal_service import multimodal_service
from backend.models.orm_models import Conversation, Message

router = APIRouter(prefix="/chat", tags=["Chat & Multimodal"])

@router.post("", response_model=ChatResponse)
def handle_chat_message(
    req: ChatRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before sending another message."
        )

    result = chat_service.process_chat(
        message_text=req.message,
        conversation_id=req.conversation_id,
        enable_emotional_support=req.enable_emotional_support,
        enable_rag=req.enable_rag,
        enable_tts=req.enable_tts,
        db=db,
        user_email=req.user_email
    )
    return result

@router.post("/image")
async def handle_image_message(
    file: UploadFile = File(...),
    prompt: str = Form("Please analyze this image and describe its key elements."),
    conversation_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Retrieve or create conversation
    conv = None
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        conv = Conversation(conversation_title=f"Image: {prompt[:30]}...")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Persist user message
    user_msg = Message(
        conversation_id=conv.id,
        message_role="user",
        message_content=f"[Uploaded Image: {file.filename}] {prompt}",
        modality="image"
    )
    db.add(user_msg)
    db.commit()

    # 3. Process vision query
    vision_res = await multimodal_service.process_image_query(file, prompt)
    response_text = vision_res["text"]

    # 4. Persist assistant message
    asst_msg = Message(
        conversation_id=conv.id,
        message_role="assistant",
        message_content=response_text,
        modality="text",
        metadata_json=json.dumps({"model": vision_res.get("model", "vision")})
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)

    return {
        "conversation_id": conv.id,
        "message_id": asst_msg.id,
        "response": response_text,
        "model_used": vision_res.get("model", "vision")
    }

@router.post("/audio")
async def handle_audio_message(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    enable_tts: bool = Form(False),
    db: Session = Depends(get_db)
):
    # 1. Transcribe audio to text
    transcript = await multimodal_service.transcribe_audio(file)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract intelligible speech from audio file."
        )

    # 2. Process through standard chat pipeline
    chat_res = chat_service.process_chat(
        message_text=transcript,
        conversation_id=conversation_id,
        enable_emotional_support=True,
        enable_rag=True,
        enable_tts=enable_tts,
        db=db
    )

    return {
        "transcript": transcript,
        **chat_res
    }

