
import pytest

from app.services.chunking_service import chunk_pages


def test_chunk_pages_splits_text_with_overlap():

    pages = [
        {
            "page_number": 1,
            "text": "ABCDEFGHIJ"
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=6,
        overlap=2
    )

    assert len(chunks) == 2
    assert chunks[0]["text"] == "ABCDEF"
    assert chunks[1]["text"] == "EFGHIJ"


def test_chunk_pages_preserves_page_numbers():

    pages = [
        {"page_number": 1, "text": "First page"},
        {"page_number": 2, "text": "Second page"}
    ]

    chunks = chunk_pages(pages, chunk_size=100, overlap=10)

    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] == 2


def test_chunk_pages_skips_empty_pages():

    pages = [
        {"page_number": 1, "text": ""},
        {"page_number": 2, "text": "   "}
    ]

    assert chunk_pages(pages) == []


def test_chunk_pages_rejects_invalid_settings():

    pages = [{"page_number": 1, "text": "Sample text"}]

    with pytest.raises(ValueError):
        chunk_pages(pages, chunk_size=0)

    with pytest.raises(ValueError):
        chunk_pages(pages, chunk_size=10, overlap=10)
