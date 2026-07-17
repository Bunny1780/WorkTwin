# WorkTwin

> Build an AI-powered organizational memory where every employee has a personalized AI agent that preserves expertise, decision-making patterns, and workflows.

## 🌟 Vision

Organizations lose valuable knowledge every time an employee changes roles or leaves the company.

WorkTwin transforms every employee's expertise into an AI agent that can continue assisting teammates, onboarding new hires, and collaborating with other agents across the organization.

The goal is not to replace employees, but to preserve institutional knowledge and enable continuous collaboration.

---

## 🎯 Core Principles

- Every employee owns one AI Agent.
- Every agent has a unique personality and working style.
- Agents learn continuously from work artifacts.
- Agents collaborate instead of working independently.
- Human approval is required for critical decisions.

---

## 🏗️ System Architecture

```text
Company
├── Employee Agents
│   ├── Product Manager Agent
│   ├── UI/UX Designer Agent
│   ├── Backend Engineer Agent
│   ├── Frontend Engineer Agent
│   ├── QA Agent
│   └── DevOps Agent
├── Organization Memory (Vector Database)
├── Knowledge Graph
├── Shared Documents & Meeting History
└── Collaboration Engine
```

---

## 🤖 Agent Blueprint (Structure)

Each employee agent contains the following components:

### 1. Identity & Expertise
- **Identity**: Name, Role, Department, Seniority.
- **Expertise**: Technical skills, Domain knowledge, Past projects, Certifications.

### 2. Persona & Style
- **Personality**: Communication style, Decision preferences, Risk tolerance, Writing style.
- **Working Style**: Planning process, Problem-solving strategy, Debugging/Documentation habits.

### 3. Long-term Memory & Tools
- **Memory**: Architecture decisions, Meeting summaries, Pull requests, Incident reports.
- **Tools**: GitHub, Slack, Notion, Jira, Google Drive, Internal APIs.

---

## 📈 Learning Sources

Agents continuously improve from:
- Code Reviews & Pull Requests
- Technical & Design Documents
- Meeting Transcripts
- Slack Discussions & Jira Tickets
- User Feedback & Incident Reports

---

## 🤝 Multi-Agent Collaboration Workflow

Instead of asking one assistant, multiple specialized agents work together to produce the final response:

```text
User ➔ PM Agent ➔ Backend Agent ➔ Frontend Agent ➔ QA Agent ➔ Final Response
```

Each agent contributes from its own expertise before producing a final answer.

---

## 🔒 Human-in-the-loop (Guardrails)

* **Agents MAY**: Draft code, Review code, Generate documentation, Suggest architecture, Answer company knowledge.
* **Agents MUST NOT**: Deploy to production, Approve pull requests, Access confidential data, Modify production systems **without human approval**.

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
3. Install Frontend dependencies: `npm install`
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
