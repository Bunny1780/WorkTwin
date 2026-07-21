## Phase 1: Environment Setup & Hello World
- [x] Initialize Python FastAPI backend environment with OpenAI SDK installed.
- [x] Create a simple `/api/chat` endpoint using OpenAI Python SDK to verify connection.
- [x] Initialize Vite + React (TypeScript) frontend environment with Tailwind CSS.
- [x] Build a basic layout with a sidebar (for agents list) and a main chat area.
- [x] Connect React frontend to FastAPI backend via fetch/axios.

## Phase 2: WorkTwin Foundation — Employee & Artifact Model (Current)
- [x] Replace the manual agent-profile model with a tenant-aware employee model: organization, employee, source identity, and lifecycle status (`active` / `departed`).
- [x] Create `work_artifacts` for normalized source records with source type, author, timestamp, project/repository context, canonical source URL, content, and access scope.
- [x] Define supported MVP artifact types: Slack message/thread, GitHub pull request/review/commit/issue, and email message/thread.
- [x] Add an explicitly derived `twin_profiles` model for evidence-based expertise, ownership, working patterns, and last refresh time. It must not be a user-authored personality form.
- [x] Define restricted versus company-shared artifact access, with email treated as a first-class source that can be restricted.

## Phase 3: Demo Data Ingestion & Organizational Memory
- [x] Create repeatable mock-data imports for Slack, GitHub, and email. Each imported record must map source identities to an employee and preserve provenance.
- [x] Enable `pgvector` and create `memory_chunks` with an artifact reference, chunk text, embedding, and access scope.
- [x] Use OpenAI `text-embedding-3-small` through the official Python SDK to embed imported artifacts and upsert the resulting chunks.
- [x] Generate or refresh each employee's derived Twin profile from their linked artifacts.
- [x] Seed a coherent demo story that includes at least one departed employee, Slack discussion, GitHub PR, and email decision trail.

## Phase 4: Evidence-Backed Twin Q&A
- [x] Build an Employee/Twin Directory that distinguishes active employees from former employees and does not expose a create/edit personality flow.
- [x] Implement a Twin query API that retrieves the selected employee's permitted memories, optionally supplements them with shared organizational memory, and sends grounded context to the OpenAI Chat Completions API.
- [x] Return source citations for every substantive Twin answer, including source type, title/context, timestamp, and canonical URL where available.
- [x] Clearly label departed-Twin responses as historical, evidence-based representations rather than real-time messages from the former employee.
- [x] Build the frontend evidence panel so users can inspect the Slack, GitHub, and email records used in an answer.

## Phase 5: Work Assistance & Guardrails
- [x] Add an explicit response mode for implementation plans and code drafts grounded in a selected Twin's historical evidence.
- [x] Define policy boundaries: Twins may draft and advise, but deployment, pull-request approval, production changes, and access to restricted artifacts require human approval.
- [x] Record the retrieved evidence and requested action with each Twin interaction for auditability.

## Phase 6: UI Polish & Hackathon Submission Prep
- [ ] Refine the directory, Twin conversation, citations, and artifact-inspection experience using Shadcn UI primitives.
- [ ] Document that live Slack, GitHub, and email OAuth/webhook connectors are post-MVP; the demo uses controlled, repeatable imports with the same ingestion contract.
- [ ] Verify that `npm run build` passes with absolute zero errors and verify environmental variables.
