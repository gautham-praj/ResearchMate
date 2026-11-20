
import httpx

from app.core.config import settings

async def generate_answer(prompt: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            settings.ollama_url,
            json=payload
        )

        response.raise_for_status()

        result = response.json()

        return result["response"]
