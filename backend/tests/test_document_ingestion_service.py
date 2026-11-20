import pytest
import asyncio

from app.services import document_ingestion_service as ingestion


def test_ingest_document_runs_complete_pipeline(
    tmp_path,
    monkeypatch
):
    pages = [
        {"page_number": 1, "text": "ResearchMate uses RAG."}
    ]

    chunks = [
        {
            "page_number": 1,
            "chunk_index": 0,
            "text": "ResearchMate uses RAG."
        }
    ]

    vectors = [[0.1, 0.2, 0.3]]

    saved = {}

    monkeypatch.setattr(
        ingestion,
        "extract_text_by_page",
        lambda path: pages
    )

    monkeypatch.setattr(
        ingestion,
        "chunk_pages",
        lambda extracted_pages: chunks
    )

    async def fake_embeddings(texts):
        assert texts == ["ResearchMate uses RAG."]
        return vectors

    monkeypatch.setattr(
        ingestion,
        "generate_embeddings",
        fake_embeddings
    )

    def fake_save_vectors(embeddings, metadata, store_dir):
        saved["vectors"] = embeddings
        saved["chunks"] = metadata
        saved["store_dir"] = store_dir

    monkeypatch.setattr(
        ingestion,
        "save_vectors",
        fake_save_vectors
    )

    result = asyncio.run(ingestion.ingest_document(
        tmp_path / "sample.pdf",
        "document-123",
        tmp_path / "vector_store"
    ))

    assert result == {
        "page_count": 1,
        "chunk_count": 1
    }

    assert saved["vectors"] == vectors
    assert saved["chunks"] == chunks
    assert saved["store_dir"] == tmp_path / "vector_store" / "document-123"