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

## Scholarly Content Firewall

Codex must treat this repository as an engineering and database-maintenance project, not as a scholarly interpretation project.

### Absolute boundary

Codex must not cross from engineering support into scholarly judgment.

The following tasks are reserved for the user and ChatGPT-based scholarly analysis:

1. reading journal articles;
2. selecting academic usage phrases;
3. judging whether a phrase is worth learning;
4. explaining argumentative function;
5. classifying scholarly usage categories;
6. defining research horizon records;
7. identifying core research questions;
8. interpreting Chinese philosophical concepts;
9. judging the significance of a paper;
10. creating or revising concept-index content;
11. filling missing scholarly metadata by inference;
12. generating new academic claims, summaries, or interpretations.

Codex may only handle these materials after the user has already supplied them in an explicit, structured form.

### Permitted Codex work

Codex may perform engineering tasks only:

1. validate JSONL format;
2. check schema compliance;
3. check duplicate IDs;
4. check missing required fields;
5. convert user-provided text into structured JSONL;
6. repair mechanical formatting errors;
7. update scripts;
8. update import workflows;
9. update Supabase sync scripts;
10. update GitHub Pages exports;
11. create logs, reports, backups, and health checks;
12. test database search and synchronization.

### Prohibited Codex behavior

Codex must never:

1. invent paper titles, authors, publication years, journal names, DOI values, page ranges, or abstracts;
2. invent original English phrases or quotations;
3. invent Chinese explanations, argumentative functions, research methods, or research significance;
4. fill empty scholarly fields by guessing;
5. rewrite scholarly interpretations to make records look more complete;
6. merge two records into a new interpretation unless the user explicitly instructs it;
7. change usage categories or research categories based on its own judgment;
8. modify `data/*.jsonl` scholarly content unless the user explicitly provides the intended content or asks for a mechanical correction;
9. silently delete, overwrite, or normalize scholarly records;
10. treat passing schema validation as proof that scholarly content is correct.

### Required behavior when content is incomplete

If Codex finds missing or ambiguous scholarly content, it must not fill the gap.

It must instead produce a report using this format:

```text
SCHOLARLY CONTENT REVIEW NEEDED

File:
Record ID:
Field:
Problem:
Why Codex cannot fix it:
Suggested user action:
```

### Mechanical correction rule

Codex may correct only mechanical issues, such as:

1. invalid JSON escaping;
2. missing commas;
3. duplicate trailing spaces;
4. inconsistent line endings;
5. invalid UTF-8 encoding;
6. filename or path errors;
7. duplicate IDs when the correct ID rule is explicitly known;
8. schema field ordering, if no content is changed.

Codex must report every mechanical correction.

### Commit rule

Any commit that touches `data/*.jsonl`, `daily/*.txt`, or scholarly content exports must include a clear statement of whether the change is:

1. mechanical formatting only;
2. user-provided content import;
3. script-generated export;
4. schema or workflow update.

If uncertain, Codex must not commit.

### Final principle

Codex is allowed to protect the database structure.

Codex is not allowed to author the database's scholarly substance.

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
