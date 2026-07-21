-- Retrieval function used by the evidence-backed Twin Q&A API. A selected
-- employee may use their own restricted evidence plus optional tenant-shared
-- evidence; restricted artifacts authored by other employees are excluded.

create or replace function public.match_twin_memory_chunks(
  query_embedding extensions.vector(1536),
  target_employee_id uuid,
  include_company_shared boolean default true,
  match_count integer default 8
)
returns table (
  artifact_id uuid,
  chunk_text text,
  source_type text,
  title text,
  source_uri text,
  occurred_at timestamptz,
  access_scope text,
  similarity double precision
)
language sql
stable
set search_path = public, extensions
as $$
  select
    artifact.id,
    chunk.chunk_text,
    artifact.source_type,
    artifact.title,
    artifact.source_uri,
    artifact.occurred_at,
    chunk.access_scope,
    1 - (chunk.embedding <=> query_embedding) as similarity
  from public.memory_chunks as chunk
  join public.work_artifacts as artifact on artifact.id = chunk.artifact_id
  join public.employees as target on target.id = target_employee_id
  where chunk.embedding is not null
    and artifact.organization_id = target.organization_id
    and (
      artifact.author_employee_id = target_employee_id
      or (include_company_shared and chunk.access_scope = 'company_shared')
    )
  order by chunk.embedding <=> query_embedding
  limit greatest(match_count, 1);
$$;

revoke all on function public.match_twin_memory_chunks(extensions.vector, uuid, boolean, integer) from public;
