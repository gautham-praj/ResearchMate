
import httpx

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ollama_service import generate_answer


router = APIRouter()


# Defines the structure of incoming chat requests
class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


@router.post("/chat")
async def chat(request: ChatRequest):

    try:
        answer = await generate_answer(request.question)

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Ollama. Is Ollama running?"
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Ollama took too long to respond."
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Ollama returned an error."
        )

    return {
        "question": request.question,
        "answer": answer
    }
