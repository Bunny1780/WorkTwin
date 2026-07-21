-- Every artifact, including email, has one explicit retrieval boundary.
-- Authorization rules are enforced by the backend retrieval pipeline; this
-- database constraint prevents imports from silently creating an unknown scope.

alter table public.work_artifacts
  drop constraint if exists work_artifacts_access_scope_check;

alter table public.work_artifacts
  add constraint work_artifacts_access_scope_check
  check (access_scope in ('company_shared', 'restricted'));

comment on column public.work_artifacts.access_scope is
  'Retrieval boundary: company_shared is eligible for tenant-wide memory; restricted requires explicit authorization. Applies equally to Slack, GitHub, and email artifacts.';
