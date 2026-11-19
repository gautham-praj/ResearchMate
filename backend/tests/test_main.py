
from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient

from app.api.routes import chat
from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_success(monkeypatch):
    mock_generate = AsyncMock(
        return_value="This is a mocked answer."
    )

    monkeypatch.setattr(
        chat,
        "generate_answer",
        mock_generate
    )

    response = client.post(
        "/chat",
        json={"question": "What is an API?"}
    )

    assert response.status_code == 200

    assert response.json() == {
        "question": "What is an API?",
        "answer": "This is a mocked answer."
    }

    mock_generate.assert_awaited_once_with(
        "What is an API?"
    )


def test_chat_empty_question():
    response = client.post(
        "/chat",
        json={"question": ""}
    )

    assert response.status_code == 422


def test_chat_ollama_unavailable(monkeypatch):
    mock_generate = AsyncMock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    monkeypatch.setattr(
        chat,
        "generate_answer",
        mock_generate
    )

    response = client.post(
        "/chat",
        json={"question": "What is an API?"}
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Could not connect to Ollama. Is Ollama running?"
    }

    mock_generate.assert_awaited_once_with(
        "What is an API?"
    )


def test_chat_ollama_timeout(monkeypatch):
    mock_generate = AsyncMock(
        side_effect=httpx.TimeoutException("Request timed out")
    )

    monkeypatch.setattr(
        chat,
        "generate_answer",
        mock_generate
    )

    response = client.post(
        "/chat",
        json={"question": "Explain artificial intelligence"}
    )

    assert response.status_code == 504

    assert response.json() == {
        "detail": "Ollama took too long to respond."
    }

    mock_generate.assert_awaited_once_with(
        "Explain artificial intelligence"
    )
