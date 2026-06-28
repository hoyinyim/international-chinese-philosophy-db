-- 001_create_core_tables.sql
-- International Chinese Philosophy Journal Database
-- Core tables for structured records and future Custom GPT Actions.

create extension if not exists vector;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ============================================================
-- 1. Papers
-- ============================================================

create table if not exists public.papers (
  paper_id text primary key,
  date date not null,
  author text not null,
  title text not null,
  year text not null,
  journal text not null,
  doi text default '',
  research_area text[] default '{}',
  keywords_en text[] default '{}',
  keywords_zh text[] default '{}',
  notes text default '',
  raw jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

drop trigger if exists set_papers_updated_at on public.papers;

create trigger set_papers_updated_at
before update on public.papers
for each row
execute function public.set_updated_at();

-- ============================================================
-- 2. Academic Usage
-- ============================================================

create table if not exists public.academic_usage (
  usage_id text primary key,
  paper_id text not null references public.papers(paper_id) on delete cascade,
  date date not null,
  author text not null,
  title text not null,
  year text not null,
  source text not null,
  original_phrase text not null,
  pragmatic_category text not null,
  chinese_explanation text not null,
  argumentative_function text not null,
  why_learnable text not null,
  transferable_context text not null,
  imitable_pattern text not null,
  cautions text not null,
  source_location text default '',
  raw jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

drop trigger if exists set_academic_usage_updated_at on public.academic_usage;

create trigger set_academic_usage_updated_at
before update on public.academic_usage
for each row
execute function public.set_updated_at();

create index if not exists academic_usage_paper_id_idx
on public.academic_usage(paper_id);

create index if not exists academic_usage_category_idx
on public.academic_usage(pragmatic_category);

-- ============================================================
-- 3. Research Horizon
-- ============================================================

create table if not exists public.research_horizon (
  horizon_id text primary key,
  paper_id text not null references public.papers(paper_id) on delete cascade,
  date date not null,
  author text not null,
  title text not null,
  year text not null,
  source text not null,
  research_topic text not null,
  research_category text not null,
  core_question text not null,
  materials text not null,
  method text not null,
  scholarly_interlocutors text not null,
  main_claim text not null,
  international_horizon text not null,
  relevance_to_my_research text not null,
  extendable_questions text not null,
  source_location text default '',
  raw jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

drop trigger if exists set_research_horizon_updated_at on public.research_horizon;

create trigger set_research_horizon_updated_at
before update on public.research_horizon
for each row
execute function public.set_updated_at();

create index if not exists research_horizon_paper_id_idx
on public.research_horizon(paper_id);

create index if not exists research_horizon_category_idx
on public.research_horizon(research_category);

-- ============================================================
-- 4. Concept Index
-- ============================================================

create table if not exists public.concept_index (
  concept_id text primary key,
  zh_term text not null,
  en_terms text[] default '{}',
  related_zh_terms text[] default '{}',
  related_en_terms text[] default '{}',
  linked_paper_ids text[] default '{}',
  linked_usage_ids text[] default '{}',
  linked_horizon_ids text[] default '{}',
  notes text default '',
  raw jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

drop trigger if exists set_concept_index_updated_at on public.concept_index;

create trigger set_concept_index_updated_at
before update on public.concept_index
for each row
execute function public.set_updated_at();

create index if not exists concept_index_zh_term_idx
on public.concept_index(zh_term);

create index if not exists concept_index_en_terms_idx
on public.concept_index using gin(en_terms);

create index if not exists concept_index_related_zh_terms_idx
on public.concept_index using gin(related_zh_terms);

-- ============================================================
-- 5. Retrieval Chunks
-- ============================================================
-- This is the future AI retrieval table.
-- embedding uses vector(1536), matching text-embedding-3-small default dimension.

create table if not exists public.retrieval_chunks (
  chunk_id text primary key,
  source_type text not null check (
    source_type in ('paper', 'academic_usage', 'research_horizon', 'concept')
  ),
  source_id text not null,
  paper_id text references public.papers(paper_id) on delete cascade,
  title text default '',
  author text default '',
  category text default '',
  concepts text[] default '{}',
  content text not null,
  metadata jsonb default '{}'::jsonb,
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

drop trigger if exists set_retrieval_chunks_updated_at on public.retrieval_chunks;

create trigger set_retrieval_chunks_updated_at
before update on public.retrieval_chunks
for each row
execute function public.set_updated_at();

create index if not exists retrieval_chunks_source_idx
on public.retrieval_chunks(source_type, source_id);

create index if not exists retrieval_chunks_paper_id_idx
on public.retrieval_chunks(paper_id);

create index if not exists retrieval_chunks_category_idx
on public.retrieval_chunks(category);

create index if not exists retrieval_chunks_concepts_idx
on public.retrieval_chunks using gin(concepts);

create index if not exists retrieval_chunks_metadata_idx
on public.retrieval_chunks using gin(metadata);

create index if not exists retrieval_chunks_embedding_idx
on public.retrieval_chunks
using hnsw (embedding vector_cosine_ops);