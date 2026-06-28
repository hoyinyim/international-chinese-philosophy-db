-- 003_create_search_functions.sql
-- Keyword search functions for AI retrieval.

create or replace function public.search_chunks_keyword(
  query_text text,
  source_filter text default null,
  limit_count int default 20
)
returns table (
  chunk_id text,
  source_type text,
  source_id text,
  paper_id text,
  title text,
  author text,
  category text,
  concepts text[],
  content text,
  metadata jsonb,
  score int
)
language sql
stable
as $$
  select
    rc.chunk_id,
    rc.source_type,
    rc.source_id,
    rc.paper_id,
    rc.title,
    rc.author,
    rc.category,
    rc.concepts,
    rc.content,
    rc.metadata,
    (
      case when rc.content ilike '%' || query_text || '%' then 10 else 0 end +
      case when rc.title ilike '%' || query_text || '%' then 8 else 0 end +
      case when rc.author ilike '%' || query_text || '%' then 6 else 0 end +
      case when rc.category ilike '%' || query_text || '%' then 5 else 0 end +
      case when array_to_string(rc.concepts, ' ') ilike '%' || query_text || '%' then 7 else 0 end
    ) as score
  from public.retrieval_chunks rc
  where
    (source_filter is null or rc.source_type = source_filter)
    and (
      rc.content ilike '%' || query_text || '%'
      or rc.title ilike '%' || query_text || '%'
      or rc.author ilike '%' || query_text || '%'
      or rc.category ilike '%' || query_text || '%'
      or array_to_string(rc.concepts, ' ') ilike '%' || query_text || '%'
    )
  order by score desc, rc.created_at desc
  limit limit_count;
$$;


create or replace function public.search_usage_keyword(
  query_text text,
  limit_count int default 20
)
returns table (
  chunk_id text,
  source_type text,
  source_id text,
  paper_id text,
  title text,
  author text,
  category text,
  concepts text[],
  content text,
  metadata jsonb,
  score int
)
language sql
stable
as $$
  select *
  from public.search_chunks_keyword(query_text, 'academic_usage', limit_count);
$$;


create or replace function public.search_horizon_keyword(
  query_text text,
  limit_count int default 20
)
returns table (
  chunk_id text,
  source_type text,
  source_id text,
  paper_id text,
  title text,
  author text,
  category text,
  concepts text[],
  content text,
  metadata jsonb,
  score int
)
language sql
stable
as $$
  select *
  from public.search_chunks_keyword(query_text, 'research_horizon', limit_count);
$$;


create or replace function public.search_concepts_keyword(
  query_text text,
  limit_count int default 20
)
returns table (
  chunk_id text,
  source_type text,
  source_id text,
  paper_id text,
  title text,
  author text,
  category text,
  concepts text[],
  content text,
  metadata jsonb,
  score int
)
language sql
stable
as $$
  select *
  from public.search_chunks_keyword(query_text, 'concept', limit_count);
$$;