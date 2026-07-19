"""FastAPI endpoints for WorkTwin."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field

from app.config import Settings, get_settings


app = FastAPI(title="WorkTwin API", version="0.1.0")


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=4_000)]


class ChatResponse(BaseModel):
    model: str
    reply: str


def get_openai_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncOpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and set it.",
        )
    return AsyncOpenAI(api_key=settings.openai_api_key)


@app.get("/health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    """Provide a non-sensitive readiness check."""
    return {
        "status": "ok",
        "openai": "configured" if settings.openai_api_key else "not_configured",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
) -> ChatResponse:
    """Verify the OpenAI connection through the official Chat Completions SDK API."""
    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": request.message}],
        )
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Unable to reach the OpenAI API.") from exc
    except APIStatusError as exc:
        raise HTTPException(status_code=exc.status_code, detail="OpenAI API request failed.") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail="OpenAI SDK request failed.") from exc

    reply = completion.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty message.")
    return ChatResponse(model=settings.openai_model, reply=reply)

