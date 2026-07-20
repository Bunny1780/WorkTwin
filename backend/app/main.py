"""FastAPI endpoints for WorkTwin."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field

from app.agents import (
    AgentProfile,
    AgentProfileCreate,
    AgentProfileUpdate,
    SupabaseAgentRepository,
    get_agents_repository,
)
from app.config import Settings, get_settings


app = FastAPI(title="WorkTwin API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=4_000)]
    agent_id: UUID | None = None


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


def format_profile_details(details: dict[str, str]) -> str:
    return "; ".join(
        f"{key.replace('_', ' ')}: {value}" for key, value in details.items() if value
    )


def build_agent_system_prompt(profile: AgentProfile) -> str:
    """Build a stable identity prompt from a configured employee-agent profile."""
    expertise = ", ".join(profile.expertise) or "Not specified"
    personality = format_profile_details(profile.personality) or "Not specified"
    working_style = format_profile_details(profile.working_style) or "Not specified"
    return (
        f"You are {profile.name}, a {profile.seniority} {profile.role} in the "
        f"{profile.department} department at WorkTwin.\n"
        "Respond as this employee agent: use the profile to guide your tone, priorities, "
        "and recommendations, while remaining helpful, accurate, and transparent about uncertainty.\n"
        f"Expertise: {expertise}.\n"
        f"Personality: {personality}.\n"
        f"Working style: {working_style}."
    )


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
    messages: list[dict[str, str]] = [{"role": "user", "content": request.message}]
    if request.agent_id:
        repository = get_agents_repository(settings)
        profile = get_agent_or_404(await repository.get_profile(request.agent_id))
        messages.insert(
            0,
            {"role": "system", "content": build_agent_system_prompt(profile)},
        )
    try:
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
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


def get_agent_or_404(profile: AgentProfile | None) -> AgentProfile:
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found.")
    return profile


@app.get("/api/agents", response_model=list[AgentProfile])
async def list_agents(
    repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)],
) -> list[AgentProfile]:
    """Return the organization's available WorkTwin agent profiles."""
    return await repository.list_profiles()


@app.get("/api/agents/{agent_id}", response_model=AgentProfile)
async def get_agent(
    agent_id: UUID,
    repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)],
) -> AgentProfile:
    """Return one agent profile."""
    return get_agent_or_404(await repository.get_profile(agent_id))


@app.post("/api/agents", response_model=AgentProfile, status_code=status.HTTP_201_CREATED)
async def create_agent(
    profile: AgentProfileCreate,
    repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)],
) -> AgentProfile:
    """Create a new employee agent profile."""
    return await repository.create_profile(profile)


@app.patch("/api/agents/{agent_id}", response_model=AgentProfile)
async def update_agent(
    agent_id: UUID,
    update: AgentProfileUpdate,
    repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)],
) -> AgentProfile:
    """Update the identity, persona, or working style of an agent."""
    return get_agent_or_404(await repository.update_profile(agent_id, update))
