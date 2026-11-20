import json

import faiss
import pytest

from app.services.vector_store_service import save_vectors


def test_save_vectors_persists_index_and_metadata(tmp_path):

    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]

    chunks = [
        {"page_number": 1, "chunk_index": 0, "text": "First chunk"},
        {"page_number": 2, "chunk_index": 0, "text": "Second chunk"}
    ]

    save_vectors(vectors, chunks, tmp_path)

    index_path = tmp_path / "index.faiss"
    metadata_path = tmp_path / "metadata.json"

    assert index_path.exists()
    assert metadata_path.exists()

    index = faiss.read_index(str(index_path))

    assert index.ntotal == 2
    assert index.d == 3

    with metadata_path.open(encoding="utf-8") as file:
        metadata = json.load(file)

    assert metadata == chunks


def test_save_vectors_rejects_mismatched_lengths(tmp_path):

    with pytest.raises(ValueError):
        save_vectors([[1.0, 0.0]], [], tmp_path)


def test_save_vectors_rejects_empty_input(tmp_path):

    with pytest.raises(ValueError):
        save_vectors([], [], tmp_path)

def test_search_vectors_returns_most_similar_chunks_first(tmp_path):

    from app.services.vector_store_service import search_vectors

    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]

    chunks = [
        {"page_number": 1, "text": "AI and machine learning"},
        {"page_number": 2, "text": "Database management"},
        {"page_number": 3, "text": "Web development"}
    ]

    save_vectors(vectors, chunks, tmp_path)

    query_vector = [0.9, 0.1, 0.0]

    results = search_vectors(query_vector, tmp_path, top_k=2)

    assert len(results) == 2
    assert results[0]["chunk"]["text"] == "AI and machine learning"
    assert results[1]["chunk"]["text"] == "Database management"
    assert results[0]["score"] > results[1]["score"]

def test_search_vectors_respects_top_k(tmp_path):

    from app.services.vector_store_service import search_vectors

    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]

    chunks = [
        {"page_number": 1, "text": "First chunk"},
        {"page_number": 2, "text": "Second chunk"},
        {"page_number": 3, "text": "Third chunk"}
    ]

    save_vectors(vectors, chunks, tmp_path)

    results = search_vectors(
        [1.0, 0.0, 0.0],
        tmp_path,
        top_k=1
    )

    assert len(results) == 1
    assert results[0]["chunk"]["text"] == "First chunk"

def test_search_vectors_raises_error_for_missing_store(tmp_path):

    from app.services.vector_store_service import search_vectors

    with pytest.raises(FileNotFoundError):
        search_vectors(
            [1.0, 0.0, 0.0],
            tmp_path
        )