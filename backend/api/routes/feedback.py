from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.orm_models import Feedback, Message
from backend.schemas.feedback_schema import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["User Feedback"])

@router.post("", response_model=FeedbackResponse)
def submit_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == data.message_id).first()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {data.message_id} not found."
        )

    feedback_record = Feedback(
        conversation_id=data.conversation_id,
        message_id=data.message_id,
        feedback_type=data.feedback_type.lower(),
        feedback_text=data.feedback_text
    )
    db.add(feedback_record)
    db.commit()
    db.refresh(feedback_record)

    return FeedbackResponse(
        id=feedback_record.id,
        status="success",
        message="Thank you for your feedback!"
    )

