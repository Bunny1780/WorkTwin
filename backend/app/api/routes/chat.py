"""Legacy OpenAI connectivity route."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, OpenAIError

from app.api.dependencies import get_openai_client, get_optional_agents_repository
from app.core.config import Settings, get_settings
from app.repositories.agents import SupabaseAgentRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_chat import build_agent_system_prompt

from .agents import get_agent_or_404


router = APIRouter(prefix="/api", tags=["legacy chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
    repository: Annotated[
        SupabaseAgentRepository | None,
        Depends(get_optional_agents_repository),
    ],
) -> ChatResponse:
    messages: list[dict[str, str]] = [{"role": "user", "content": request.message}]
    if request.agent_id:
        if repository is None:
            raise HTTPException(
                status_code=503,
                detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
            )
        profile = get_agent_or_404(await repository.get_profile(request.agent_id))
        messages.insert(0, {"role": "system", "content": build_agent_system_prompt(profile)})
    try:
        completion = await client.chat.completions.create(model=settings.openai_model, messages=messages)
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
