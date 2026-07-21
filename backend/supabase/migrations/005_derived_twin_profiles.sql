-- Derived, evidence-backed Work Twin summaries. These fields are written by
-- the profile-generation pipeline; they are intentionally not user-authored
-- persona settings.

create table if not exists public.twin_profiles (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid not null unique references public.employees(id) on delete cascade,
  expertise jsonb not null default '[]'::jsonb,
  ownership jsonb not null default '[]'::jsonb,
  working_patterns jsonb not null default '{}'::jsonb,
  communication_summary text,
  source_artifact_count integer not null default 0
    check (source_artifact_count >= 0),
  source_last_occurred_at timestamptz,
  derived_at timestamptz not null default now(),
  generation_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists twin_profiles_derived_at_idx
  on public.twin_profiles (derived_at desc);

drop trigger if exists twin_profiles_set_updated_at on public.twin_profiles;
create trigger twin_profiles_set_updated_at
before update on public.twin_profiles
for each row execute function public.set_updated_at();

alter table public.twin_profiles enable row level security;

-- Browser clients do not write Twin profiles. The backend generation pipeline
-- refreshes them from permitted work artifacts and records its metadata.
