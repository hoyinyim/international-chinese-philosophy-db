-- 002_enable_rls.sql
-- Enable Row Level Security.
-- Data will be written and read by trusted server-side scripts or Edge Functions.

alter table public.papers enable row level security;
alter table public.academic_usage enable row level security;
alter table public.research_horizon enable row level security;
alter table public.concept_index enable row level security;
alter table public.retrieval_chunks enable row level security;