-- pgvector-backed memory chunks for evidence retrieval. The embedding pipeline
-- writes the nullable embedding field after chunking source artifacts.

create extension if not exists vector with schema extensions;

create table if not exists public.memory_chunks (
  id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references public.work_artifacts(id) on delete cascade,
  chunk_index integer not null check (chunk_index >= 0),
  chunk_text text not null check (char_length(chunk_text) > 0),
  embedding extensions.vector(1536),
  access_scope text not null
    check (access_scope in ('company_shared', 'restricted')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (artifact_id, chunk_index)
);

create index if not exists memory_chunks_artifact_id_idx
  on public.memory_chunks (artifact_id);

create index if not exists memory_chunks_access_scope_idx
  on public.memory_chunks (access_scope);

create index if not exists memory_chunks_embedding_cosine_idx
  on public.memory_chunks using hnsw (embedding extensions.vector_cosine_ops);

drop trigger if exists memory_chunks_set_updated_at on public.memory_chunks;
create trigger memory_chunks_set_updated_at
before update on public.memory_chunks
for each row execute function public.set_updated_at();

alter table public.memory_chunks enable row level security;

-- Browser clients do not access raw chunks. The backend retrieval pipeline
-- filters by artifact access scope before returning grounded evidence.
