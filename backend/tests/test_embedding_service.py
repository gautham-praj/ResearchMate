
import pytest

from app.services.embedding_service import generate_embeddings


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_generate_embeddings_sends_batch_to_ollama(monkeypatch):

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "embeddings": [
                    [0.1, 0.2, 0.3],
                    [0.4, 0.5, 0.6]
                ]
            }

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            pass
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json):
            captured["url"] = url
            captured["payload"] = json
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.embedding_service.httpx.AsyncClient",
        FakeAsyncClient
    )

    texts = ["First chunk", "Second chunk"]

    result = await generate_embeddings(texts)

    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]

    assert captured["url"] == "http://localhost:11434/api/embed"
    assert captured["payload"]["model"] == "nomic-embed-text"
    assert captured["payload"]["input"] == texts


@pytest.mark.anyio
async def test_generate_embeddings_returns_empty_list_for_empty_input(monkeypatch):

    def unexpected_client(*args, **kwargs):
        raise AssertionError("HTTP client should not be created")

    monkeypatch.setattr(
        "app.services.embedding_service.httpx.AsyncClient",
        unexpected_client
    )

    result = await generate_embeddings([])

    assert result == []
