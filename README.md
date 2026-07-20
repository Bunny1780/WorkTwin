# WorkTwin

> An AI-powered organizational memory SaaS that creates an evidence-backed Work Twin for every employee from the work they actually do.

## 🌟 Vision

Organizations lose valuable knowledge every time an employee changes roles or leaves the company.

WorkTwin connects to company work artifacts and continuously builds a Work Twin for each employee. A Twin preserves demonstrable expertise, decision-making context, technical ownership, and collaboration patterns so teammates can retrieve institutional knowledge long after a role changes or an employee leaves.

The goal is not to replace employees, but to preserve institutional knowledge and enable continuous collaboration.

---

## 🎯 Core Principles

- Each employee has one Work Twin, created from their work artifacts rather than from a manually written persona.
- A Twin's expertise, working style, and communication patterns are derived and refreshed from evidence.
- Every substantive answer is grounded in retrievable company memory and returns source citations.
- Departed employees remain available as clearly labelled historical Twins, subject to company permissions.
- Human approval is required for critical or external actions.

---

## 🏗️ System Architecture

```text
Organization (SaaS tenant)
├── Source connections / demo imports
│   ├── Slack: messages and threads
│   ├── GitHub: pull requests, reviews, commits, and issues
│   └── Email: formal decisions, cross-team communication, and handovers
├── Employee directory
│   └── active and departed employees, linked to source identities
├── Organizational memory (Supabase + pgvector)
│   └── normalized artifacts, memory chunks, embeddings, access scope, and provenance
├── Work Twin profiles
│   └── derived expertise, ownership, decision patterns, and communication summary
└── Twin interaction layer
    └── cited Q&A, implementation planning, and code drafts with human approval
```

---

## 🤖 Work Twin model

Each Twin is an evidence-backed representation of an employee's work context. It is not a separately trained model and does not require the employee to manually author a personality.

### 1. Employee identity and lifecycle
- **Identity**: Name, role, department, and linked Slack/GitHub/email identities.
- **Lifecycle**: `active` or `departed`. Departed Twins and their permitted historical memory remain part of the organization.

### 2. Derived work profile
- **Expertise and ownership**: Repositories, systems, projects, technical topics, and recurring responsibilities inferred from work artifacts.
- **Working patterns**: Decision preferences, planning and debugging habits, and communication summary inferred from evidence and refreshable as data changes.

### 3. Long-term, cited memory
- **Memory**: Original Slack discussions, GitHub activity, emails, documents, decisions, and incident records, with author, timestamp, source URL, and access scope.
- **Retrieval**: Queries retrieve relevant employee and shared organizational memory before generating a response; answers expose their sources.

---

## 📈 Learning sources

Twins continuously update from connected or imported work artifacts:

- Slack messages and threads
- GitHub pull requests, reviews, commits, and issues
- Email conversations, decisions, approvals, and handovers
- Technical and design documents, meeting transcripts, Jira tickets, feedback, and incident reports

For the hackathon MVP, these sources are represented through curated, repeatable demo imports. Production connectors and webhooks follow the same ingestion contract.

---

## 💬 Core user experience

Users select an employee from the directory and ask that person's Twin about prior decisions or request a work artifact such as an implementation plan or code draft:

```text
User ➔ Employee Twin ➔ retrieve employee + permitted organization memory ➔ cited response / draft
```

Example: a teammate can ask a departed backend engineer's Twin why a retry limit was selected, inspect the Slack and pull-request evidence, then request a compatible webhook implementation plan. The Twin never implies that it is the former employee responding in real time.

---

## 🔒 Human-in-the-loop (Guardrails)

* **Twins MAY**: Answer company-knowledge questions with citations, draft code, review code, generate documentation, and suggest architecture.
* **Twins MUST NOT**: Deploy to production, approve pull requests, bypass artifact access controls, or modify production systems **without human approval**.
* **Email and sensitive artifacts**: Retrieval must respect an artifact's company-shared or restricted access scope; private or restricted email is never indiscriminately available to every Twin.

---

## 🛠️ Tech Stack & Getting Started

### Tech Stack
- **Frontend**: React (Vite, TypeScript, Tailwind CSS, Shadcn UI)
- **Backend**: Python (FastAPI)
- **AI Core**: Official OpenAI Python SDK (GPT-5.6 / Assistants API)
- **Database**: Supabase (PostgreSQL + pgvector)

### Development Setup
1. Clone the repository.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Set up `.env` with `OPENAI_API_KEY` and `SUPABASE_URL`.

### Backend (Phase 1)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload
```

Set `OPENAI_API_KEY` in the root `.env`, then send a request to `POST /api/chat`:

```json
{"message":"Hello, WorkTwin!"}
```

### Frontend (Phase 1)

In a second terminal, start the Vite development server:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the
FastAPI server at `http://127.0.0.1:8000`.

### MVP status

The existing profile-editor and generic-chat prototype is being superseded by the data-driven Work Twin MVP described above. See [`TODO.md`](TODO.md) for the approved implementation sequence. No production Slack, GitHub, or email connector is required for the hackathon demo; the MVP starts with controlled imports that preserve source provenance.
