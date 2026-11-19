from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.connection import get_db
from backend.models.orm_models import Conversation, Message
from backend.schemas.chat_schema import ConversationSummary, ConversationDetail, MessageDetail

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationSummary])
def list_conversations(
    user_email: Optional[str] = Query(None, description="Filter conversations by user email"),
    db: Session = Depends(get_db)
):
    query = (
        db.query(
            Conversation.id,
            Conversation.conversation_title,
            Conversation.user_email,
            Conversation.created_at,
            Conversation.updated_at,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message, Conversation.id == Message.conversation_id)
    )

    if user_email:
        query = query.filter(Conversation.user_email == user_email)

    results = (
        query.group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    summaries = []
    for r in results:
        summaries.append(
            ConversationSummary(
                id=r.id,
                conversation_title=r.conversation_title,
                user_email=r.user_email or "guest@jivan.ai",
                created_at=r.created_at.isoformat(),
                updated_at=r.updated_at.isoformat(),
                message_count=r.message_count
            )
        )
    return summaries

@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found."
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    msg_details = [
        MessageDetail(
            id=m.id,
            conversation_id=m.conversation_id,
            message_role=m.message_role,
            message_content=m.message_content,
            modality=m.modality,
            metadata_json=m.metadata_json,
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]

    return ConversationDetail(
        id=conv.id,
        conversation_title=conv.conversation_title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=msg_details
    )

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found."
        )

    db.delete(conv)
    db.commit()
    return {"message": f"Conversation {conversation_id} and all messages deleted successfully."}

