-- Foundation for data-driven Work Twins. Run after 001_agent_profiles.sql.
-- The legacy agent_profiles table remains untouched while the application is
-- migrated to the evidence-backed employee model in subsequent phases.

create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 160),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.employees (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 120),
  role text not null check (char_length(role) between 1 and 120),
  department text not null check (char_length(department) between 1 and 120),
  employment_status text not null default 'active'
    check (employment_status in ('active', 'departed')),
  departed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    (employment_status = 'active' and departed_at is null)
    or (employment_status = 'departed' and departed_at is not null)
  )
);

create table if not exists public.employee_source_identities (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid not null references public.employees(id) on delete cascade,
  provider text not null check (provider in ('slack', 'github', 'email')),
  external_id text not null check (char_length(external_id) between 1 and 320),
  external_handle text,
  email_address text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (employee_id, provider),
  unique (provider, external_id)
);

create index if not exists employees_organization_id_idx
  on public.employees (organization_id);

create index if not exists employees_organization_status_idx
  on public.employees (organization_id, employment_status);

create index if not exists employee_source_identities_employee_id_idx
  on public.employee_source_identities (employee_id);

drop trigger if exists organizations_set_updated_at on public.organizations;
create trigger organizations_set_updated_at
before update on public.organizations
for each row execute function public.set_updated_at();

drop trigger if exists employees_set_updated_at on public.employees;
create trigger employees_set_updated_at
before update on public.employees
for each row execute function public.set_updated_at();

drop trigger if exists employee_source_identities_set_updated_at on public.employee_source_identities;
create trigger employee_source_identities_set_updated_at
before update on public.employee_source_identities
for each row execute function public.set_updated_at();

alter table public.organizations enable row level security;
alter table public.employees enable row level security;
alter table public.employee_source_identities enable row level security;

-- Browser clients do not access these tables directly. The backend service-role
-- key performs controlled access until tenant authentication is implemented.
