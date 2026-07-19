-- Run this migration in Supabase before enabling the Agent Profiles API.
create table if not exists public.agent_profiles (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 120),
  role text not null check (char_length(role) between 1 and 120),
  department text not null check (char_length(department) between 1 and 120),
  seniority text not null check (char_length(seniority) between 1 and 80),
  expertise jsonb not null default '[]'::jsonb,
  personality jsonb not null default '{}'::jsonb,
  working_style jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists agent_profiles_set_updated_at on public.agent_profiles;
create trigger agent_profiles_set_updated_at
before update on public.agent_profiles
for each row execute function public.set_updated_at();

alter table public.agent_profiles enable row level security;

-- Browser clients never access this table directly; the backend service-role key
-- performs controlled API access. Add user-facing policies in a future auth phase.
