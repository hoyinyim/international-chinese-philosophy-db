# Supabase Edge Function: `search`

This Edge Function provides a single HTTP search endpoint for the International Chinese Philosophy Journal Database.

It is designed to be used by Custom GPT Actions. The function receives a query, searches the Supabase `retrieval_chunks` table through PostgreSQL RPC search functions, and returns the most relevant records.

---

## Endpoint

```text
https://<project-ref>.supabase.co/functions/v1/search
```

For this project:

```text
https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search
```

---

## Request Method

```text
POST
```

---

## Request Headers

```text
Content-Type: application/json
X-GPT-API-Key: <GPT_ACTION_API_KEY>
```

`X-GPT-API-Key` must match the `GPT_ACTION_API_KEY` secret configured in Supabase Edge Function secrets.

---

## Request Body

```json
{
  "query": "勞思光",
  "mode": "all",
  "limit": 10
}
```

---

## Request Fields

| Field   | Type   | Required | Description                                                  |
| ------- | ------ | -------- | ------------------------------------------------------------ |
| `query` | string | yes      | Search query. Can be Chinese or English.                     |
| `mode`  | string | no       | Search mode. Defaults to `all`.                              |
| `limit` | number | no       | Maximum number of results. Defaults to `10`; capped at `30`. |

---

## Search Modes

| Mode       | Description                           |
| ---------- | ------------------------------------- |
| `all`      | Search all retrieval chunks.          |
| `usage`    | Search academic usage records only.   |
| `horizon`  | Search research horizon records only. |
| `concepts` | Search concept index records only.    |

---

## Response Example

```json
{
  "query": "勞思光",
  "mode": "all",
  "limit": 10,
  "count": 3,
  "results": [
    {
      "chunk_id": "concept__C0001",
      "source_type": "concept",
      "source_id": "C0001",
      "paper_id": "P20260628-AMES2022-001",
      "title": "",
      "author": "",
      "category": "concept",
      "concepts": ["勞思光", "Lao Sze-Kwang", "Lao Siguang"],
      "content": "中文概念：勞思光\n英文術語：Lao Sze-Kwang、Lao Siguang...",
      "metadata": {},
      "score": 10
    }
  ]
}
```

---

## Environment Variables

Supabase provides these automatically inside Edge Functions:

```text
SUPABASE_URL
SUPABASE_SECRET_KEYS
```

This project also requires one custom secret:

```text
GPT_ACTION_API_KEY
```

Legacy Supabase projects may also expose:

```text
SUPABASE_SERVICE_ROLE_KEY
```

The function supports both the new `SUPABASE_SECRET_KEYS` environment variable and the legacy `SUPABASE_SERVICE_ROLE_KEY`.

---

## Required Secrets

In Supabase Dashboard, configure:

```text
Edge Functions
→ Secrets
```

Add:

```text
Name: GPT_ACTION_API_KEY
Value: <your-private-action-key>
```

Do not expose this value publicly. It will later be used in the Custom GPT Action authentication header.

---

## Authentication Model

This function does not rely on Supabase user JWT authentication.

Instead, it checks the request header:

```text
X-GPT-API-Key
```

The value must match:

```text
GPT_ACTION_API_KEY
```

For this reason, the Edge Function should be deployed with JWT verification disabled.

---

## Deploy Setting

When deploying this function, disable JWT verification:

```text
Verify JWT: off
```

If using Supabase CLI:

```powershell
supabase functions deploy search --no-verify-jwt
```

---

## Internal RPC Functions

This Edge Function calls one of the following PostgreSQL functions depending on `mode`:

| Mode       | RPC Function              |
| ---------- | ------------------------- |
| `all`      | `search_chunks_keyword`   |
| `usage`    | `search_usage_keyword`    |
| `horizon`  | `search_horizon_keyword`  |
| `concepts` | `search_concepts_keyword` |

These RPC functions search the `retrieval_chunks` table.

---

## PowerShell Test

Set the test API key:

```powershell
$env:GPT_ACTION_API_KEY="your-private-action-key"
```

Prepare headers:

```powershell
$headers = @{
  "Content-Type" = "application/json"
  "X-GPT-API-Key" = $env:GPT_ACTION_API_KEY
}
```

Test general search:

```powershell
$body = @{
  query = "勞思光"
  mode = "all"
  limit = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

Test academic usage search:

```powershell
$body = @{
  query = "Far from"
  mode = "usage"
  limit = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

Test research horizon search:

```powershell
$body = @{
  query = "儒家"
  mode = "horizon"
  limit = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

Test concept search:

```powershell
$body = @{
  query = "天地"
  mode = "concepts"
  limit = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

---

## Notes

* Do not expose `SUPABASE_SECRET_KEYS`, `SUPABASE_SERVICE_ROLE_KEY`, or `GPT_ACTION_API_KEY`.
* Do not commit `.env` to GitHub.
* This function is intended for server-side retrieval only.
* Custom GPT Actions should call this endpoint through the configured authentication header.
* The function currently performs keyword search through PostgreSQL RPC functions. Vector search can be added later by extending `retrieval_chunks.embedding` and adding embedding-based RPC functions.
