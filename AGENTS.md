# AGENTS.md

## Project identity

This repository is `international-chinese-philosophy-db`.

It is an academic database project for international English-language Chinese philosophy journal articles. The project maintains two main scholarly databases:

1. International Chinese Philosophy Academic Usage Database
2. International Chinese Philosophy Research Horizon Database

The database is used by:
- local JSONL data files;
- GitHub Pages data export;
- AI-ready corpus exports;
- Supabase PostgreSQL;
- Supabase Edge Function API;
- Custom GPT Actions.

## Core principle

Codex is responsible for engineering workflow, validation, automation, synchronization, testing, reporting, and repository maintenance.

Codex must not independently create or alter scholarly interpretations, academic usage records, research horizon records, or concept index content unless the user explicitly provides the content or explicitly asks for a mechanical format conversion.

## Never do

1. Never read, print, modify, commit, or push `.env`.
2. Never ask the user to paste `SUPABASE_SERVICE_ROLE_KEY`, `GPT_ACTION_API_KEY`, or any secret.
3. Never modify `data/*.jsonl` scholarly content unless the user explicitly asks for a controlled import, validation, repair, or format conversion.
4. Never invent paper metadata, paper titles, authors, journal names, publication years, concepts, quotations, or scholarly claims.
5. Never automatically commit or push unless the user explicitly asks.
6. Never enable `-AutoCommit` by default.
7. Never remove existing data records without explicit user confirmation.
8. Never change ID conventions without explicit user confirmation.

## Preferred Python command

On this Windows machine, use:

`py -3`

Do not use plain `python`, because it may point to the Windows App Execution Alias and return exit code 9009.

## Main workflow script

The daily update script is:

`scripts/daily_update.ps1`

It should:
1. check `incoming/`;
2. run `scripts/import_and_update.ps1`;
3. validate JSONL;
4. check data integrity;
5. build website data;
6. build AI export corpus;
7. sync to Supabase;
8. test Supabase search;
9. write logs;
10. show Git status.

The script must stop on error and must not commit or push unless `-AutoCommit` is explicitly provided.

## Files Codex may modify

Codex may modify:
- `scripts/`
- `schema/`
- `docs/`
- `ai_exports/`
- `supabase/`
- `ai_actions/`
- `templates/`
- `README.md`
- `AGENTS.md`

Codex may create:
- `logs/`
- `reports/`
- `backups/`
- `incoming/processed/`
- `incoming/error/`

## Files requiring caution

Codex must treat these as high-risk:
- `data/papers.jsonl`
- `data/academic_usage.jsonl`
- `data/research_horizon.jsonl`
- `data/concept_index.jsonl`
- `.env`

## Testing requirements

After changing workflow code, Codex should provide exact test commands. Preferred tests:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\daily_update.ps1" -SkipSupabase
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\daily_update.ps1"
py -3 scripts\sync_to_supabase.py
py -3 scripts\test_supabase_search.py
git status --short
```
