import hashlib
import numpy as np
from typing import List, Union
from backend.core.config import settings
from backend.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.dim = 384  # Standard dense embedding dimension

    def get_embedding(self, text: str) -> np.ndarray:
        return self.get_embeddings([text])[0]

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dim), dtype=np.float32)

        # 1. Try Google Gemini Embeddings
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                vectors = []
                for t in texts:
                    res = client.models.embed_content(
                        model=settings.GEMINI_EMBEDDING_MODEL,
                        contents=t
                    )
                    # Reshape or take embedding values
                    vec = np.array(res.embedding.values, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    vectors.append(vec)
                return np.vstack(vectors)
            except Exception as e:
                logger.warning(f"Gemini embedding API failed ({e}). Falling back to local semantic encoder.")

        # 2. Try OpenAI Embeddings
        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                resp = client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=texts
                )
                vectors = [np.array(item.embedding, dtype=np.float32) for item in resp.data]
                normalized = []
                for vec in vectors:
                    norm = np.linalg.norm(vec)
                    normalized.append(vec / norm if norm > 0 else vec)
                return np.vstack(normalized)
            except Exception as e:
                logger.warning(f"OpenAI embedding API failed ({e}). Falling back to local semantic encoder.")

        # 3. Deterministic Local Semantic Dense Encoder (Zero-Network fallback)
        return self._local_semantic_encoder(texts)

    def _local_semantic_encoder(self, texts: List[str]) -> np.ndarray:
        """
        Generates robust, normalized dense 384-d semantic vectors using multi-ngram
        feature hashing. Yields cosine similarities correlating with lexical & n-gram overlap.
        """
        vectors = []
        for text in texts:
            vec = np.zeros(self.dim, dtype=np.float32)
            cleaned = text.lower().strip()
            tokens = cleaned.split()
            # Unigram + bigram hashing
            ngrams = tokens + [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
            if not ngrams:
                ngrams = [cleaned]

            for gram in ngrams:
                h = int(hashlib.sha256(gram.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)

        return np.vstack(vectors)

embedding_service = EmbeddingService()

