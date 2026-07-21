-- Immutable-enough audit trail for evidence-backed Twin assistance. Browser
-- clients cannot access interaction prompts, responses, or retrieved evidence.

create table if not exists public.twin_interactions (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid not null references public.employees(id) on delete cascade,
  requested_action text not null check (char_length(requested_action) between 1 and 4000),
  response_mode text not null default 'advice'
    check (response_mode in ('advice', 'implementation_plan', 'code_draft')),
  include_company_shared boolean not null default true,
  retrieved_evidence jsonb not null default '[]'::jsonb,
  response_text text not null check (char_length(response_text) > 0),
  created_at timestamptz not null default now()
);

create index if not exists twin_interactions_employee_created_at_idx
  on public.twin_interactions (employee_id, created_at desc);

alter table public.twin_interactions enable row level security;

-- The backend service-role owns writes and later audit review. No browser RLS
-- policy is created because interaction logs can include sensitive evidence.
