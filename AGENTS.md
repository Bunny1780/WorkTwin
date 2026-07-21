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
  - A feature branch represents one independently reviewable, cohesive feature. It may include multiple tightly coupled `TODO.md` items, but must not combine unrelated concerns.
  - Keep commits small and logical (normally 3-5 files per commit). A feature branch may contain multiple structured commits; do not force an entire feature into one commit.
  - Automatically create a feature branch (e.g., `feature/phaseX-feature-name`) and make clean, structured commits as each logical increment is completed.
* **Branching Strategy (Git Flow)**:
  - The `master` (or `main`) branch is STRICTLY reserved for stable production-ready code.
  - The `develop` branch is our primary active development workspace. All new feature branches (`feature/xxx`) must branch off from `develop` and must be merged back into `develop` upon successful completion.
  - Never commit directly to `master`.
  - Before rebasing a feature branch, switch to `develop` and run `git pull origin develop`; then switch back to the feature branch and rebase it onto the updated local `develop` branch.
  - Use local rebase to incorporate `develop` into feature branches; merge pull requests into `develop` on GitHub using merge commits.
  - If rebasing a previously pushed branch requires `git push --force-with-lease`, obtain explicit user approval before running that command.
* **Automated Pull Request Workflow**:
  - Every completed cohesive feature branch must be pushed to GitHub (`origin/feature/xxx`).
  - The Agent must programmatically generate a comprehensive, highly professional English PR description directed at the `develop` branch.
  - The PR must contain sections for Description, Key Changes, and a DoD Checklist.
  - Merge the PR only after ensuring the build passes on the branch.
  - Delete the remote feature branch after a successful merge unless the user explicitly asks to retain it.

## 5. Definition of Done (DoD)
A task is completed only when:
1. The React app builds successfully without TypeScript errors.
2. The FastAPI server runs smoothly with correct OpenAI SDK integrations.
3. The progress is marked as [DONE] in `TODO.md`.
