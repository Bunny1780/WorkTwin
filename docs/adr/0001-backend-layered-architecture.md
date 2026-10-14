# ADR 0001: Layer the FastAPI Backend by Responsibility

## Status

Accepted.

## Context

The original FastAPI application placed routes, request and response models, configuration, Supabase access, OpenAI orchestration, and CLI worker logic in a small number of modules. This was practical for the hackathon MVP, but makes OAuth connectors and other new product surfaces harder to implement and test independently.

## Decision

Organize the backend into the following layers:

- `app/api/routes`: HTTP route declarations only.
- `app/api/dependencies`: reusable FastAPI dependency providers.
- `app/core`: cross-cutting configuration and security helpers.
- `app/schemas`: Pydantic API contracts.
- `app/repositories`: Supabase persistence adapters.
- `app/services`: business rules and OpenAI orchestration.
- top-level worker modules: stable CLI entry points that compose a repository, settings, and service.

Existing endpoint paths, response contracts, and worker commands remain stable. The legacy agent-profile API remains isolated so it can be retired independently of the evidence-backed Twin experience.

## Consequences

- Routes and services can be tested with dependency overrides and fakes without live external services.
- New connectors, including Gmail OAuth, have clear locations for route, token persistence adapter, synchronization service, and schemas.
- A no-agent legacy chat request must not require Supabase configuration; selecting an agent continues to require it.
