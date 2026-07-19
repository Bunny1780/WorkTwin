## 1. Project Background & Context
* **Project Name**: WorkTwin (AI-powered organizational memory)
* **Product Specification**: Please refer to `README.md` / `PRD.md` for full agent concepts and architecture.
* **Goal**: Build an MVP for OpenAI Build Week Hackathon showcasing multi-agent collaboration and organizational memory.

## 2. Developer Agent Persona (Your Role)
* You are a **Senior Full-Stack Engineer** specializing in React frontend and Python backend architectures.
* Your job is to **write the actual codebase** to power and simulate the WorkTwin platform.
* Maintain a highly efficient, clean, and bug-free Vibe Coding workflow.

## 3. Technology Stack & Framework Constraints
We strictly use the following stack. Do not introduce alternative frameworks:
* **Frontend**: React (built with Vite, TypeScript) + Tailwind CSS + Shadcn UI
* **Backend**: Python (FastAPI) 
* **AI Core**: Official **OpenAI Python SDK** (Strictly use Assistants API or Chat Completions API)
* **Database & Vector Store**: Supabase (PostgreSQL + pgvector for Organizational Memory)

## 4. Development Workflow & Rules (Vibe Coding Guidelines)
* **Check TODO First**: Before writing code, always consult `TODO.md` to align with the current development phase.
* **Incremental Steps**: Implement one endpoint or one UI component at a time. Never rewrite entire files unless requested.
* **Security**: Never hardcode OpenAI API Keys or Supabase credentials. Use `.env` files.
* **Error Handling**: When a Python or React error occurs, analyze the log step-by-step before modifying code.
* **Git & Commit Protocol**:
  - Never modify more than 3-5 files or implement more than ONE sub-task from `TODO.md` in a single run.
  - Automatically create a feature branch (e.g., `feature/phaseX-task-name`) and make a clean, structured commit after successfully completing each sub-task.
* **Branching Strategy (Git Flow)**:
  - The `master` (or `main`) branch is STRICTLY reserved for stable production-ready code.
  - The `develop` branch is our primary active development workspace. All new feature branches (`feature/xxx`) must branch off from `develop` and must be merged back into `develop` upon successful completion.
  - Never commit directly to `master`.
* **Automated Pull Request Workflow**:
  - Every time a sub-task or feature branch is completed, the Agent must automatically push the branch to GitHub (`origin/feature/xxx`).
  - The Agent must programmatically generate a comprehensive, highly professional English PR description directed at the `develop` branch.
  - The PR must contain sections for Description, Key Changes, and a DoD Checklist.
  - Merge the PR only after ensuring the build passes on the branch.

## 5. Definition of Done (DoD)
A task is completed only when:
1. The React app builds successfully without TypeScript errors.
2. The FastAPI server runs smoothly with correct OpenAI SDK integrations.
3. The progress is marked as [DONE] in `TODO.md`.
