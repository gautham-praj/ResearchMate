
import httpx

from app.core.config import settings


async def generate_embeddings(texts: list[str]) -> list[list[float]]:

    if not texts:
        return []

    payload = {
        "model": settings.ollama_embedding_model,
        "input": texts
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            settings.ollama_embedding_url,
            json=payload
        )

        response.raise_for_status()

        result = response.json()

        return result["embeddings"]
