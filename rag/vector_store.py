import os
import re
import json
import numpy as np
from typing import List, Dict, Any, Optional
from backend.core.config import settings
from backend.core.logging import logger

class VectorStoreManager:
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or settings.VECTOR_STORE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index_file = os.path.join(self.storage_dir, "vectors.npy")
        self.metadata_file = os.path.join(self.storage_dir, "metadata.json")

        self.embeddings: np.ndarray = np.empty((0, 384), dtype=np.float32)
        self.metadata: List[Dict[str, Any]] = []
        self.load()

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Appends chunks and corresponding embeddings to the in-memory vector store,
        then persists to disk.
        """
        if len(chunks) == 0:
            return

        if self.embeddings.shape[0] == 0:
            self.embeddings = embeddings.astype(np.float32)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings.astype(np.float32)])

        self.metadata.extend(chunks)
        self.save()
        logger.info(f"Vector store indexed {len(chunks)} new chunks. Total indexed: {len(self.metadata)}")

    def get_chunks_for_document(self, doc_identifier: str) -> List[Dict[str, Any]]:
        """
        Returns all indexed chunks for a given document name or ID.
        """
        clean_id = doc_identifier.lower().strip()
        matched = []
        for idx, meta in enumerate(self.metadata):
            m_id = str(meta.get("document_id", "")).lower()
            m_name = str(meta.get("document_name", "")).lower()
            if clean_id in m_id or clean_id in m_name or m_name in clean_id:
                chunk_data = dict(meta)
                chunk_data["score"] = 1.0
                matched.append(chunk_data)
        return matched

    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
        threshold: float = 0.15,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid similarity search (vector cosine + lexical keyword matching).
        """
        if len(self.metadata) == 0:
            return []

        # 1. Cosine similarity
        cosine_scores = np.zeros(len(self.metadata), dtype=np.float32)
        if self.embeddings.shape[0] == len(self.metadata) and query_embedding is not None:
            cosine_scores = np.dot(self.embeddings, query_embedding)

        # 2. Lexical analysis if query text is available
        query_words = set()
        is_analysis_mode = False
        target_doc_name = None

        if query_text:
            cleaned_q = query_text.lower()
            query_words = set(re.findall(r"\w+", cleaned_q))
            # Check for analysis/summary intents
            analysis_keywords = {"summarize", "summary", "overview", "analyze", "analysis", "insights", "breakdown", "findings", "report", "pdf", "document"}
            if query_words & analysis_keywords:
                is_analysis_mode = True

            # Check if query specifically names an indexed document
            for meta in self.metadata:
                d_name = meta.get("document_name", "").lower()
                d_base = d_name.rsplit(".", 1)[0]
                if d_name in cleaned_q or d_base in cleaned_q:
                    target_doc_name = d_name
                    break

        final_scores = []
        for idx, meta in enumerate(self.metadata):
            cos_score = float(cosine_scores[idx]) if idx < len(cosine_scores) else 0.0
            score = max(0.0, cos_score)

            if query_words:
                doc_name_clean = meta.get("document_name", "").lower()
                content_clean = meta.get("content", "").lower()
                doc_tokens = set(re.findall(r"\w+", doc_name_clean))
                content_tokens = set(re.findall(r"\w+", content_clean))

                # Exact document target match gets massive priority
                if target_doc_name and doc_name_clean == target_doc_name:
                    score += 2.0
                else:
                    # Lexical overlap
                    name_overlap = len(query_words & doc_tokens)
                    content_overlap = len(query_words & content_tokens)
                    score += (name_overlap * 0.4) + min(0.6, content_overlap * 0.1)

            # In analysis mode with no specific target, give recency/baseline boost
            if is_analysis_mode and not target_doc_name:
                score += 0.25

            final_scores.append((score, idx))

        # Sort descending by score
        final_scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, idx in final_scores:
            if score < threshold and len(results) > 0:
                break
            chunk_data = dict(self.metadata[idx])
            chunk_data["score"] = round(float(score), 4)
            results.append(chunk_data)
            if len(results) >= top_k:
                break

        return results

    def delete_document(self, document_id: str) -> int:
        """
        Removes all vectors and metadata associated with a document_id.
        """
        if self.embeddings.shape[0] == 0:
            return 0

        keep_indices = []
        keep_metadata = []
        removed_count = 0

        for idx, meta in enumerate(self.metadata):
            if meta.get("document_id") == document_id:
                removed_count += 1
            else:
                keep_indices.append(idx)
                keep_metadata.append(meta)

        if removed_count > 0:
            if keep_indices:
                self.embeddings = self.embeddings[keep_indices]
                self.metadata = keep_metadata
            else:
                self.embeddings = np.empty((0, 384), dtype=np.float32)
                self.metadata = []
            self.save()
            logger.info(f"Deleted {removed_count} chunks for document {document_id}")

        return removed_count

    def get_total_chunks(self) -> int:
        return len(self.metadata)

    def save(self):
        try:
            np.save(self.index_file, self.embeddings)
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                self.embeddings = np.load(self.index_file)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded existing vector store with {len(self.metadata)} chunks.")
            except Exception as e:
                logger.warning(f"Could not load vector store files ({e}). Initializing empty store.")
                self.embeddings = np.empty((0, 384), dtype=np.float32)
                self.metadata = []

vector_store_manager = VectorStoreManager()
