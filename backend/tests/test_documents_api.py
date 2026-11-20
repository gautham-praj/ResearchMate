
import pymupdf
import pytest

from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app)


def create_test_pdf():

    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "ResearchMate test document"
        )
        return document.tobytes()


def test_upload_valid_pdf(tmp_path, monkeypatch):

    monkeypatch.setattr(settings, "documents_dir", tmp_path)

    monkeypatch.setattr(
        settings,
        "vector_store_dir",
        tmp_path / "vector_store"
    )

    monkeypatch.setattr(
        "app.api.routes.documents.ingest_document",
        AsyncMock(return_value={
            "page_count": 1,
            "chunk_count": 1
        })
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                create_test_pdf(),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["page_count"] == 1
    assert data["chunk_count"] == 1
    assert len(data["document_id"]) == 32

    saved_file = tmp_path / f"{data['document_id']}.pdf"
    assert saved_file.exists()


def test_upload_invalid_pdf(tmp_path, monkeypatch):

    monkeypatch.setattr(settings, "documents_dir", tmp_path)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "fake.pdf",
                b"This is not a PDF.",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400
    assert "not a valid PDF" in response.json()["detail"]

    assert list(tmp_path.iterdir()) == []


def test_upload_oversized_file(tmp_path, monkeypatch):

    monkeypatch.setattr(settings, "documents_dir", tmp_path)
    monkeypatch.setattr(settings, "max_upload_size_bytes", 10)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.pdf",
                b"A" * 100,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 413

    assert list(tmp_path.iterdir()) == []

def test_upload_cleans_up_when_ingestion_fails(tmp_path, monkeypatch):

    documents_dir = tmp_path / "documents"
    vector_store_dir = tmp_path / "vector_store"

    monkeypatch.setattr(settings, "documents_dir", documents_dir)
    monkeypatch.setattr(settings, "vector_store_dir", vector_store_dir)

    async def fake_ingestion(pdf_path, document_id, store_dir):

        partial_store = store_dir / document_id
        partial_store.mkdir(parents=True)
        (partial_store / "partial.txt").write_text("partial data")

        raise ValueError("PDF contains no extractable text.")

    monkeypatch.setattr(
        "app.api.routes.documents.ingest_document",
        AsyncMock(side_effect=fake_ingestion)
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                create_test_pdf(),
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422
    assert list(documents_dir.iterdir()) == []
    assert list(vector_store_dir.iterdir()) == []