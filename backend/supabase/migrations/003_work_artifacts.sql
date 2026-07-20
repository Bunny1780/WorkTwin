-- Normalized organizational-memory records. Source-type and access-scope
-- allowlists are introduced in separate migrations so this foundation can be
-- deployed before connector-specific behavior is implemented.

create table if not exists public.work_artifacts (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  author_employee_id uuid references public.employees(id) on delete set null,
  author_source_identity_id uuid references public.employee_source_identities(id) on delete set null,
  source_type text not null check (char_length(source_type) between 1 and 80),
  source_external_id text not null check (char_length(source_external_id) between 1 and 320),
  source_uri text not null check (char_length(source_uri) between 1 and 2048),
  title text,
  content text not null check (char_length(content) > 0),
  project_context jsonb not null default '{}'::jsonb,
  source_metadata jsonb not null default '{}'::jsonb,
  access_scope text not null default 'company_shared'
    check (char_length(access_scope) between 1 and 80),
  occurred_at timestamptz not null,
  ingested_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, source_type, source_external_id)
);

create index if not exists work_artifacts_organization_occurred_at_idx
  on public.work_artifacts (organization_id, occurred_at desc);

create index if not exists work_artifacts_author_employee_id_idx
  on public.work_artifacts (author_employee_id);

create index if not exists work_artifacts_author_source_identity_id_idx
  on public.work_artifacts (author_source_identity_id);

drop trigger if exists work_artifacts_set_updated_at on public.work_artifacts;
create trigger work_artifacts_set_updated_at
before update on public.work_artifacts
for each row execute function public.set_updated_at();

alter table public.work_artifacts enable row level security;

-- Browser clients do not access artifacts directly. The backend service-role
-- key enforces tenant and artifact-access rules until user authentication is
-- introduced.
