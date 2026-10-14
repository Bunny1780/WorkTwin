"""Legacy agent-profile routes retained during the evidence-backed migration."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_agents_repository
from app.repositories.agents import SupabaseAgentRepository
from app.schemas.agents import AgentProfile, AgentProfileCreate, AgentProfileUpdate


router = APIRouter(prefix="/api/agents", tags=["legacy agents"])


def get_agent_or_404(profile: AgentProfile | None) -> AgentProfile:
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found.")
    return profile


@router.get("", response_model=list[AgentProfile])
async def list_agents(repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)]) -> list[AgentProfile]:
    return await repository.list_profiles()


@router.get("/{agent_id}", response_model=AgentProfile)
async def get_agent(agent_id: UUID, repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)]) -> AgentProfile:
    return get_agent_or_404(await repository.get_profile(agent_id))


@router.post("", response_model=AgentProfile, status_code=status.HTTP_201_CREATED)
async def create_agent(profile: AgentProfileCreate, repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)]) -> AgentProfile:
    return await repository.create_profile(profile)


@router.patch("/{agent_id}", response_model=AgentProfile)
async def update_agent(agent_id: UUID, update: AgentProfileUpdate, repository: Annotated[SupabaseAgentRepository, Depends(get_agents_repository)]) -> AgentProfile:
    return get_agent_or_404(await repository.update_profile(agent_id, update))
