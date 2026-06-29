# Custom GPT Action Setup

This file explains how to connect a Custom GPT to the International Chinese Philosophy Journal Database search API.

API endpoint:
https://huufvwzqocfiinzlygbn.supabase.co/functions/v1/search

Authentication:
Use API Key authentication with a custom header.

Header name:
X-GPT-API-Key

Header value:
Use the same GPT_ACTION_API_KEY stored in Supabase Edge Function Secrets.

Search modes:

all
Search all retrieval chunks.

usage
Search academic usage records only.

horizon
Search research horizon records only.

concepts
Search concept index records only.

Recommended GPT behavior:

The Custom GPT should call the search API whenever the user asks about academic usage, research horizons, article records, concepts, authors, categories, or reusable English academic phrasing.

When using returned records, the GPT should preserve the paper title and author when available, identify the source type, and avoid inventing article content not present in the database.

For academic usage records, explain the original phrase, usage category, Chinese meaning, argumentative function, transferable writing context, imitation pattern, and cautions.

For research horizon records, explain the research topic, research category, core question, textual materials, method, scholarly conversation, main claim, international academic horizon, future research relevance, and possible extension questions.

If the returned records are insufficient, the GPT should state that the current database does not yet contain enough evidence.

Suggested Custom GPT instruction:

Use the International Chinese Philosophy Journal Database through the search action whenever the user asks about academic usage, research horizons, concepts, articles, authors, or reusable English academic phrasing. Always ground answers in returned database records. Do not invent article content or bibliographic details. If search results are insufficient, state that the current database does not contain enough evidence.

Phase 5 status:
This file supports the first Custom GPT Action connection.

Next phase:
Phase 6: Configure the Custom GPT Action in ChatGPT Builder.