from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class DocumentUploadResponse(BaseModel):
    document_id: str
    document_name: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str

class DocumentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Semantic search query")
    top_k: Optional[int] = Field(4, ge=1, le=20)
    threshold: Optional[float] = Field(0.55, ge=0.0, le=1.0)

class DocumentChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    score: float

class DocumentQueryResponse(BaseModel):
    query: str
    total_results: int
    results: List[DocumentChunkResult]

class DocumentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_name: str
    file_type: str
    file_size: int
    chunk_count: int
    processing_status: str
    created_at: str
