-- Restrict the WorkTwin MVP to the artifact types supported by its import
-- contract. Additional connector types require an explicit future migration.

alter table public.work_artifacts
  drop constraint if exists work_artifacts_source_type_check;

alter table public.work_artifacts
  add constraint work_artifacts_source_type_check
  check (
    source_type in (
      'slack_message',
      'slack_thread',
      'github_pull_request',
      'github_review',
      'github_commit',
      'github_issue',
      'email_message',
      'email_thread'
    )
  );
