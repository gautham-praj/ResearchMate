
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


def test_answer_document_question_rejects_irrelevant_chunks(tmp_path, monkeypatch):
    retrieved_chunks = [
        {
            "score": 0.43,
            "chunk": {
                "page_number": 29,
                "chunk_index": 0,
                "text": "Information about Graph RAG."
            }
        }
    ]

    monkeypatch.setattr(
        qa, "generate_embeddings", AsyncMock(return_value=[[0.1, 0.2]])
    )
    monkeypatch.setattr(
        qa, "search_vectors",
        lambda query_vector, store_dir, top_k: retrieved_chunks
    )

    generation_mock = AsyncMock()
    monkeypatch.setattr(qa, "generate_answer", generation_mock)

    result = asyncio.run(
        qa.answer_document_question(
            question="What is global warming?",
            document_id="document-123",
            vector_store_dir=tmp_path
        )
    )

    assert result["sources"] == []
    assert "couldn't find relevant information" in result["answer"]
    generation_mock.assert_not_awaited()


def test_answer_document_question_keeps_only_relevant_chunks(
    tmp_path, monkeypatch
):
    retrieved_chunks = [
        {
            "score": 0.72,
            "chunk": {
                "page_number": 25,
                "chunk_index": 0,
                "text": "Graph RAG uses graph-based retrieval."
            }
        },
        {
            "score": 0.43,
            "chunk": {
                "page_number": 29,
                "chunk_index": 1,
                "text": "Unrelated passage."
            }
        }
    ]

    monkeypatch.setattr(
        qa, "generate_embeddings", AsyncMock(return_value=[[0.1, 0.2]])
    )
    monkeypatch.setattr(
        qa, "search_vectors",
        lambda query_vector, store_dir, top_k: retrieved_chunks
    )

    generation_mock = AsyncMock(return_value="Graph RAG uses graph-based retrieval.")
    monkeypatch.setattr(qa, "generate_answer", generation_mock)

    result = asyncio.run(
        qa.answer_document_question(
            question="How does Graph RAG work?",
            document_id="document-123",
            vector_store_dir=tmp_path
        )
    )

    assert len(result["sources"]) == 1
    assert result["sources"][0]["page_number"] == 25
    assert "Graph RAG uses graph-based retrieval" in result["sources"][0]["text"]

    prompt = generation_mock.await_args.args[0]
    assert "Graph RAG uses graph-based retrieval" in prompt
    assert "Unrelated passage" not in prompt
