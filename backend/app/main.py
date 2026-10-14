"""FastAPI application assembly for WorkTwin."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import agents, chat, health, twins
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title="WorkTwin API", version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health.router)
    application.include_router(twins.router)
    application.include_router(chat.router)
    application.include_router(agents.router)
    return application


app = create_app()
