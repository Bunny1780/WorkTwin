"""Evidence-backed Twin directory and query routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI

from app.api.dependencies import get_openai_client, get_twin_query_repository, get_twin_repository
from app.core.config import Settings, get_settings
from app.repositories.twin_queries import SupabaseTwinQueryRepository
from app.repositories.twins import SupabaseTwinRepository
from app.schemas.twins import TwinDirectoryEntry, TwinQueryRequest, TwinQueryResponse
from app.services.twin_queries import TwinQueryService


router = APIRouter(prefix="/api/twins", tags=["twins"])


@router.get("", response_model=list[TwinDirectoryEntry])
async def list_twins(repository: Annotated[SupabaseTwinRepository, Depends(get_twin_repository)]) -> list[TwinDirectoryEntry]:
    return await repository.list_directory()


@router.post("/{employee_id}/query", response_model=TwinQueryResponse)
async def query_twin(employee_id: UUID, request: TwinQueryRequest, settings: Annotated[Settings, Depends(get_settings)], client: Annotated[AsyncOpenAI, Depends(get_openai_client)], repository: Annotated[SupabaseTwinQueryRepository, Depends(get_twin_query_repository)]) -> TwinQueryResponse:
    return await TwinQueryService(repository, client, settings.openai_model).answer(employee_id, request)
