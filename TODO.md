## Phase 1: Environment Setup & Hello World
- [x] Initialize Python FastAPI backend environment with OpenAI SDK installed.
- [x] Create a simple `/api/chat` endpoint using OpenAI Python SDK to verify connection.
- [x] Initialize Vite + React (TypeScript) frontend environment with Tailwind CSS.
- [x] Build a basic layout with a sidebar (for agents list) and a main chat area.
- [x] Connect React frontend to FastAPI backend via fetch/axios.

## Phase 2: Agent Profiles & Personalization (Current)
- [x] Set up Supabase tables for Agent Profiles (Identity, Personality, Role).
- [x] Create Python APIs to fetch, create, and update agent configurations.
- [x] Build React UI components for the "Agent Directory Sidebar" and "Create/Edit Agent Panel" to dynamically fetch, create, and update configurations through the FastAPI backend.
- [x] **[Core Integration]** Implement dynamic System Prompts using the OpenAI SDK in the backend, ensuring each chat session with a specific agent strictly mirrors its distinct communication style (e.g., strict QA Agent vs. timeline-driven PM Agent).

## Phase 3: Organizational Memory & Knowledge Retrieval (Vector Store)
- [ ] Enable the `pgvector` extension in Supabase and create an `organization_memory` table for text embeddings.
- [ ] Define a minimal Knowledge Graph model linking agents, documents, projects, and decisions; record relationships alongside organizational memory.
- [ ] Implement backend endpoint: `POST /api/memory/upload` to ingest text and documents with source metadata (`source_type`, source URL, author, timestamp, project). Support demo imports for PRs/code reviews, technical/design documents, meeting transcripts, Slack/Jira discussions, user feedback, and incident reports.
- [ ] Utilize OpenAI's `text-embedding-3-small` via the Python SDK to generate embeddings and upsert them into Supabase.
- [ ] Implement a RAG (Retrieval-Augmented Generation) pipeline: look up historical company context from the vector database before routing queries to the agents and return source citations/snippets with answers.
- [ ] Document that live GitHub, Slack, Notion, Jira, Google Drive, and internal API connectors are post-MVP; use imported or seeded data for the hackathon demo.

## Phase 4: Multi-Agent Collaboration Workflow (The Wow-Factor)
- [ ] **[Hackathon Hero Feature]** Implement a sequential multi-agent orchestration API:
  - Pipeline complex user prompts through: PM Agent ➔ Backend Agent ➔ Frontend Agent ➔ QA Agent.
  - Dynamically chain inputs and outputs so the next agent inherits the cumulative context.
- [ ] Define the above as the MVP default pipeline; allow other employee-agent roles (such as UI/UX and DevOps) to remain independently usable until dynamic workflow composition is added.
- [ ] Design a "Live Workflow Visualizer" canvas in React (active nodes light up dynamically as the backend processes, showing status like `PM Agent is drafting specs...`).

## Phase 5: Human-in-the-Loop & Clearances
- [ ] Define high-risk action policies (production deployment, pull-request approval, confidential-data access, and production-system modification) that require explicit human approval.
- [ ] Implement an interception mechanism on the backend to pause the multi-agent execution if a decision requires critical clearance, persisting the workflow run and approval status.
- [ ] Build a polished approval prompt modal in React with explicit `[Approve]` and `[Reject]` actions to resume or halt the workflow.

## Phase 6: UI Polish & Hackathon Submission Prep
- [ ] Refine the design using premium UI components (e.g., Shadcn UI primitives) into a high-fidelity dark-themed enterprise dashboard.
- [ ] Seed the Supabase database with a rich, curated dataset of mock company history for a flawless live demo presentation.
- [ ] Verify that `npm run build` passes with absolute zero errors and verify environmental variables.
