import pytest
import numpy as np
from rag.chunking import RecursiveCharacterChunker
from rag.embeddings import embedding_service
from rag.vector_store import VectorStoreManager

def test_recursive_chunker():
    chunker = RecursiveCharacterChunker(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Artificial Intelligence is a field of computer science.\n\n"
        "It focuses on creating systems capable of performing tasks that typically require human intelligence. "
        "These include visual perception, speech recognition, decision-making, and translation between languages."
    )
    chunks = chunker.chunk_document(sample_text)
    assert len(chunks) > 0
    assert all("content" in c and "index" in c for c in chunks)
    for c in chunks:
        assert len(c["content"]) <= 120

def test_embedding_service():
    texts = ["Hello world", "Artificial intelligence and machine learning"]
    embeddings = embedding_service.get_embeddings(texts)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384
    # Check normalization
    norm0 = np.linalg.norm(embeddings[0])
    assert pytest.approx(norm0, 0.01) == 1.0

def test_vector_store_manager(tmp_path):
    store = VectorStoreManager(storage_dir=str(tmp_path))
    chunks = [
        {"chunk_id": "c1", "document_id": "d1", "document_name": "ai.txt", "chunk_index": 0, "content": "Machine learning and deep neural networks."},
        {"chunk_id": "c2", "document_id": "d1", "document_name": "ai.txt", "chunk_index": 1, "content": "Cooking recipes and Italian pasta dishes."}
    ]
    emb = embedding_service.get_embeddings([c["content"] for c in chunks])
    store.add_chunks(chunks, emb)

    assert store.get_total_chunks() == 2

    # Query matching ML
    query_vec = embedding_service.get_embedding("deep learning neural net")
    results = store.similarity_search(query_vec, top_k=1, threshold=0.0)
    assert len(results) == 1
    assert "neural" in results[0]["content"]

    # Delete
    deleted = store.delete_document("d1")
    assert deleted == 2
    assert store.get_total_chunks() == 0

