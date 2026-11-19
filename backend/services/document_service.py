import os
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.logging import logger
from backend.core.security import sanitize_filename, validate_file_upload, ALLOWED_DOCUMENT_EXTENSIONS
from backend.models.orm_models import Document, DocumentChunk
from rag.chunking import RecursiveCharacterChunker
from rag.embeddings import embedding_service
from rag.vector_store import vector_store_manager

class DocumentService:
    def __init__(self):
        self.chunker = RecursiveCharacterChunker(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP
        )

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extracts text from PDF or TXT documents."""
        if file_type == "pdf":
            text_parts = []
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text:
                        text_parts.append(page_text)
                doc.close()
                return "\n\n".join(text_parts)
            except Exception as e:
                logger.error(f"PyMuPDF PDF extraction failed for {file_path}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to parse PDF document: {str(e)}"
                )
        elif file_type == "txt":
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"TXT file reading failed for {file_path}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to read TXT file: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_type}"
            )

    async def process_document_upload(self, file: UploadFile, db: Session) -> Dict[str, Any]:
        """
        Validates, saves, extracts, chunks, embeds, and indexes an uploaded document.
        """
        ext = validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS)
        file_type = ext.replace(".", "")
        safe_name = sanitize_filename(file.filename or f"doc_{file_type}")
        
        # Save file to upload directory
        saved_file_path = os.path.join(settings.UPLOAD_DIR, safe_name)
        file_bytes = await file.read()
        file_size = len(file_bytes)

        # Check max size
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)

        # 1. Create Document record in DB
        doc_record = Document(
            document_name=safe_name,
            file_type=file_type,
            file_path=saved_file_path,
            file_size=file_size,
            processing_status="pending"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        try:
            # 2. Extract Text
            extracted_text = self.extract_text(saved_file_path, file_type)
            if not extracted_text.strip():
                raise ValueError("Document contains no readable text content.")

            # 3. Chunk Text
            raw_chunks = self.chunker.chunk_document(extracted_text)
            if not raw_chunks:
                raise ValueError("Document could not be divided into chunks.")

            chunk_texts = [c["content"] for c in raw_chunks]

            # 4. Generate Embeddings
            embeddings = embedding_service.get_embeddings(chunk_texts)

            # 5. Store chunks in DB and prepare vector store entries
            vector_chunks_meta = []
            for i, chunk_info in enumerate(raw_chunks):
                vec_ref = f"{doc_record.id}_{chunk_info['index']}"
                chunk_record = DocumentChunk(
                    document_id=doc_record.id,
                    chunk_index=chunk_info["index"],
                    chunk_content=chunk_info["content"],
                    vector_reference=vec_ref
                )
                db.add(chunk_record)

                vector_chunks_meta.append({
                    "chunk_id": vec_ref,
                    "document_id": doc_record.id,
                    "document_name": safe_name,
                    "chunk_index": chunk_info["index"],
                    "content": chunk_info["content"]
                })

            # 6. Index in Vector Store
            vector_store_manager.add_chunks(vector_chunks_meta, embeddings)

            # 7. Update Document status
            doc_record.chunk_count = len(raw_chunks)
            doc_record.processing_status = "indexed"
            db.commit()
            db.refresh(doc_record)

            logger.info(f"Successfully processed and indexed document '{safe_name}' with {len(raw_chunks)} chunks.")

            return {
                "document_id": doc_record.id,
                "document_name": doc_record.document_name,
                "file_type": doc_record.file_type,
                "file_size": doc_record.file_size,
                "chunk_count": doc_record.chunk_count,
                "status": doc_record.processing_status
            }

        except Exception as e:
            db.rollback()
            doc_record.processing_status = "failed"
            db.commit()
            logger.error(f"Error processing document {safe_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(e)}"
            )

    def delete_document(self, document_id: str, db: Session) -> bool:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        # Remove file from disk
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                logger.warning(f"Could not remove file {doc.file_path}: {e}")

        # Remove from vector store
        vector_store_manager.delete_document(document_id)

        # Delete from DB
        db.delete(doc)
        db.commit()
        return True

document_service = DocumentService()
