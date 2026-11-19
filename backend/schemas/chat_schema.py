from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message text")
    conversation_id: Optional[str] = Field(None, description="Optional conversation UUID to resume context")
    user_email: Optional[str] = Field("guest@jivan.ai", description="User login email ID")
    enable_emotional_support: bool = Field(True, description="Enable emotional empathy analysis & guidance")
    enable_rag: bool = Field(True, description="Enable retrieval-augmented knowledge search")
    enable_tts: bool = Field(False, description="Generate audio speech response (TTS)")

class CitationItem(BaseModel):
    document_name: str
    chunk_index: int
    content: str
    score: float

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    intent: str
    citations: List[CitationItem] = []
    audio_base64: Optional[str] = None
    emotional_support: bool = False
    model_used: str
    specialist: Optional[str] = None
    generated_file: Optional[Dict[str, Any]] = None

class MessageDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    message_role: str
    message_content: str
    modality: str
    metadata_json: Optional[str] = None
    created_at: str

class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_title: str
    user_email: Optional[str] = "guest@jivan.ai"
    created_at: str
    updated_at: str
    message_count: int

class ConversationDetail(BaseModel):
    id: str
    conversation_title: str
    created_at: str
    updated_at: str
    messages: List[MessageDetail] = []
