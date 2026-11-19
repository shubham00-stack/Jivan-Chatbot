from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.orm_models import Document
from backend.schemas.document_schema import (
    DocumentUploadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentChunkResult,
    DocumentItem
)
from backend.services.document_service import document_service
from backend.services.rag_service import rag_service

router = APIRouter(prefix="/documents", tags=["Knowledge Base & RAG"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    result = await document_service.process_document_upload(file, db)
    return result

@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    results = []
    for f in files:
        try:
            res = await document_service.process_document_upload(f, db)
            results.append({"success": True, "file": f.filename, "data": res})
        except Exception as e:
            results.append({"success": False, "file": f.filename, "error": str(e)})
    return results

@router.post("/query", response_model=DocumentQueryResponse)
def query_documents(
    req: DocumentQueryRequest,
):
    chunks = rag_service.retrieve_relevant_chunks(
        query=req.query,
        top_k=req.top_k or 4,
        threshold=req.threshold or 0.55
    )
    formatted = [
        DocumentChunkResult(
            chunk_id=c.get("chunk_id", ""),
            document_id=c.get("document_id", ""),
            document_name=c.get("document_name", ""),
            chunk_index=c.get("chunk_index", 0),
            content=c.get("content", ""),
            score=c.get("score", 0.0)
        )
        for c in chunks
    ]
    return DocumentQueryResponse(
        query=req.query,
        total_results=len(formatted),
        results=formatted
    )

@router.get("", response_model=List[DocumentItem])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        DocumentItem(
            id=d.id,
            document_name=d.document_name,
            file_type=d.file_type,
            file_size=d.file_size,
            chunk_count=d.chunk_count,
            processing_status=d.processing_status,
            created_at=d.created_at.isoformat()
        )
        for d in docs
    ]

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    deleted = document_service.delete_document(document_id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )
    return {"message": "Document and associated vectors deleted successfully.", "document_id": document_id}

