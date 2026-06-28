const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-gpt-api-key",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

type SearchMode = "all" | "usage" | "horizon" | "concepts";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json; charset=utf-8",
    },
  });
}

function getRpcName(mode: SearchMode): string {
  if (mode === "usage") return "search_usage_keyword";
  if (mode === "horizon") return "search_horizon_keyword";
  if (mode === "concepts") return "search_concepts_keyword";
  return "search_chunks_keyword";
}

function getSupabaseKey(): string {
  const legacyKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legacyKey && legacyKey.length > 0) {
    return legacyKey;
  }

  const secretKeysJson = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (!secretKeysJson) {
    return "";
  }

  try {
    const parsed = JSON.parse(secretKeysJson);

    if (typeof parsed === "string") {
      return parsed;
    }

    if (parsed && typeof parsed === "object") {
      const values = Object.values(parsed);
      for (const value of values) {
        if (
          typeof value === "string" &&
          (value.startsWith("sb_secret_") || value.startsWith("eyJ"))
        ) {
          return value;
        }
      }
    }
  } catch (_error) {
    return "";
  }

  return "";
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return jsonResponse(
      {
        error: "Method not allowed. Use POST.",
      },
      405,
    );
  }

  const expectedApiKey = Deno.env.get("GPT_ACTION_API_KEY") ?? "";
  const providedApiKey =
    req.headers.get("x-gpt-api-key") ??
    req.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ??
    "";

  if (!expectedApiKey || providedApiKey !== expectedApiKey) {
    return jsonResponse(
      {
        error: "Unauthorized.",
      },
      401,
    );
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
  const supabaseKey = getSupabaseKey();

  if (!supabaseUrl || !supabaseKey) {
    return jsonResponse(
      {
        error: "Missing Supabase environment variables.",
        has_supabase_url: Boolean(supabaseUrl),
        has_supabase_key: Boolean(supabaseKey),
      },
      500,
    );
  }

  let body: {
    query?: string;
    mode?: SearchMode;
    limit?: number;
  };

  try {
    body = await req.json();
  } catch (_error) {
    return jsonResponse(
      {
        error: "Invalid JSON body.",
      },
      400,
    );
  }

  const query = String(body.query ?? "").trim();
  const mode = (body.mode ?? "all") as SearchMode;
  const limit = Math.min(Math.max(Number(body.limit ?? 10), 1), 30);

  if (!query) {
    return jsonResponse(
      {
        error: "Missing query.",
      },
      400,
    );
  }

  if (!["all", "usage", "horizon", "concepts"].includes(mode)) {
    return jsonResponse(
      {
        error: "Invalid mode. Use all, usage, horizon, or concepts.",
      },
      400,
    );
  }

  const rpcName = getRpcName(mode);

  const rpcArgs =
    mode === "all"
      ? {
          query_text: query,
          source_filter: null,
          limit_count: limit,
        }
      : {
          query_text: query,
          limit_count: limit,
        };

  const rpcUrl = `${supabaseUrl}/rest/v1/rpc/${rpcName}`;

  const rpcResponse = await fetch(rpcUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "apikey": supabaseKey,
      "Authorization": `Bearer ${supabaseKey}`,
    },
    body: JSON.stringify(rpcArgs),
  });

  const responseText = await rpcResponse.text();

  if (!rpcResponse.ok) {
    return jsonResponse(
      {
        error: "Supabase RPC error.",
        status: rpcResponse.status,
        rpc_name: rpcName,
        details: responseText,
      },
      500,
    );
  }

  let data: unknown;

  try {
    data = JSON.parse(responseText);
  } catch (_error) {
    return jsonResponse(
      {
        error: "Failed to parse Supabase RPC response.",
        details: responseText,
      },
      500,
    );
  }

  const results = Array.isArray(data) ? data : [];

  return jsonResponse({
    query,
    mode,
    limit,
    count: results.length,
    results,
  });
});