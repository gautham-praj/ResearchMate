
import httpx
import pytest

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

DOCUMENT_ID = "a" * 32

ENDPOINT = f"/documents/{DOCUMENT_ID}/ask"


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_success(mock_answer):

    mock_answer.return_value = {
        "answer": "The seminar discusses artificial intelligence.",
        "sources": [
            {
                "page_number": 2,
                "chunk_index": 0,
                "score": 0.91,
                "text": "Artificial intelligence is the main topic."
            }
        ]
    }

    response = client.post(
        ENDPOINT,
        json={"question": "What is the seminar about?"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == DOCUMENT_ID
    assert data["answer"] == "The seminar discusses artificial intelligence."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["page_number"] == 2

    mock_answer.assert_awaited_once()


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_rejects_invalid_document_id(mock_answer):

    response = client.post(
        "/documents/invalid-id/ask",
        json={"question": "What is this document about?"}
    )

    assert response.status_code == 404

    mock_answer.assert_not_awaited()


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_returns_404_when_vector_store_is_missing(mock_answer):

    mock_answer.side_effect = FileNotFoundError(
        "Vector store does not exist."
    )

    response = client.post(
        ENDPOINT,
        json={"question": "What is this document about?"}
    )

    assert response.status_code == 404


def test_ask_document_rejects_blank_question():

    response = client.post(
        ENDPOINT,
        json={"question": "   "}
    )

    assert response.status_code == 422


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_handles_ollama_connection_error(mock_answer):

    mock_answer.side_effect = httpx.ConnectError(
        "Ollama unavailable."
    )

    response = client.post(
        ENDPOINT,
        json={"question": "Explain the main topic."}
    )

    assert response.status_code == 503


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_handles_ollama_timeout(mock_answer):

    mock_answer.side_effect = httpx.TimeoutException(
        "Ollama timed out."
    )

    response = client.post(
        ENDPOINT,
        json={"question": "Explain the main topic."}
    )

    assert response.status_code == 504


@patch(
    "app.api.routes.documents.answer_document_question",
    new_callable=AsyncMock
)
def test_ask_document_handles_ollama_http_error(mock_answer):

    request = httpx.Request("POST", "http://localhost:11434/api/generate")

    response_error = httpx.Response(
        500,
        request=request
    )

    mock_answer.side_effect = httpx.HTTPStatusError(
        "Ollama returned an error.",
        request=request,
        response=response_error
    )

    response = client.post(
        ENDPOINT,
        json={"question": "Explain the main topic."}
    )

    assert response.status_code == 502
