
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.services import document_qa_service as qa


def test_build_rag_prompt_includes_question_and_document_context():

    prompt = qa.build_rag_prompt(
        question="What is artificial intelligence?",
        retrieved_chunks=[
            {
                "score": 0.95,
                "chunk": {
                    "page_number": 3,
                    "chunk_index": 0,
                    "text": "Artificial intelligence enables machines to perform tasks."
                }
            }
        ]
    )

    assert "What is artificial intelligence?" in prompt
    assert "Page: 3" in prompt
    assert "Artificial intelligence enables machines" in prompt
    assert "untrusted source material" in prompt


def test_answer_document_question_returns_answer_and_sources(
    tmp_path,
    monkeypatch
):

    retrieved_chunks = [
        {
            "score": 0.95,
            "chunk": {
                "page_number": 3,
                "chunk_index": 0,
                "text": "Artificial intelligence enables machines to perform tasks."
            }
        }
    ]

    embedding_mock = AsyncMock(return_value=[[0.1, 0.2]])
    search_mock = lambda query_vector, store_dir, top_k: retrieved_chunks
    generation_mock = AsyncMock(
        return_value="AI enables machines to perform tasks."
    )

    monkeypatch.setattr(qa, "generate_embeddings", embedding_mock)
    monkeypatch.setattr(qa, "search_vectors", search_mock)
    monkeypatch.setattr(qa, "generate_answer", generation_mock)

    result = asyncio.run(
        qa.answer_document_question(
            question="What is AI?",
            document_id="document-123",
            vector_store_dir=tmp_path,
            top_k=3
        )
    )

    embedding_mock.assert_awaited_once_with(["What is AI?"])
    generation_mock.assert_awaited_once()

    assert result["answer"] == "AI enables machines to perform tasks."
    assert result["sources"] == [
        {
            "page_number": 3,
            "chunk_index": 0,
            "score": 0.95,
            "text": "Artificial intelligence enables machines to perform tasks."
        }
    ]


def test_answer_document_question_handles_empty_retrieval(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        qa,
        "generate_embeddings",
        AsyncMock(return_value=[[0.1, 0.2]])
    )

    monkeypatch.setattr(
        qa,
        "search_vectors",
        lambda query_vector, store_dir, top_k: []
    )

    generation_mock = AsyncMock()
    monkeypatch.setattr(qa, "generate_answer", generation_mock)

    result = asyncio.run(
        qa.answer_document_question(
            question="What is AI?",
            document_id="document-123",
            vector_store_dir=tmp_path
        )
    )

    assert result["sources"] == []
    assert "couldn't find relevant information" in result["answer"]
    generation_mock.assert_not_awaited()


@pytest.mark.parametrize(
    "embedding_result",
    [
        [],
        [[0.1, 0.2], [0.3, 0.4]]
    ]
)
def test_answer_document_question_rejects_invalid_embedding_count(
    tmp_path,
    monkeypatch,
    embedding_result
):

    monkeypatch.setattr(
        qa,
        "generate_embeddings",
        AsyncMock(return_value=embedding_result)
    )

    with pytest.raises(
        ValueError,
        match="Expected exactly one embedding"
    ):
        asyncio.run(
            qa.answer_document_question(
                question="What is AI?",
                document_id="document-123",
                vector_store_dir=tmp_path
            )
        )
