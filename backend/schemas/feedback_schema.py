from typing import Optional
from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    conversation_id: str = Field(..., description="Target conversation UUID")
    message_id: str = Field(..., description="Target message UUID")
    feedback_type: str = Field(..., description="'like' or 'dislike'")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional text comment")

class FeedbackResponse(BaseModel):
    id: str
    status: str
    message: str

