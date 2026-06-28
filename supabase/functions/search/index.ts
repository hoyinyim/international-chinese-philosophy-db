import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-gpt-api-key",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

type SearchMode = "all" | "usage" | "horizon" | "concepts";

interface SearchRequest {
  query?: string;
  mode?: SearchMode;
  limit?: number;
}

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

  const supabaseUrl = Deno.env.get("SUPABASE_URL");

function getSupabaseSecretKey(): string | null {
  const legacyKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legacyKey) {
    return legacyKey;
  }

  const secretKeysJson = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (!secretKeysJson) {
    return null;
  }

  try {
    const parsed = JSON.parse(secretKeysJson);

    if (typeof parsed === "string") {
      return parsed;
    }

    if (parsed && typeof parsed === "object") {
      const values = Object.values(parsed);
      const secretKey = values.find(
        (value) =>
          typeof value === "string" &&
          (value.startsWith("sb_secret_") || value.startsWith("eyJ")),
      );

      if (typeof secretKey === "string") {
        return secretKey;
      }
    }

    return null;
  } catch (_error) {
    return null;
  }
}

const supabaseSecretKey = getSupabaseSecretKey();

if (!supabaseUrl || !supabaseSecretKey) {
  return jsonResponse(
    {
      error: "Missing Supabase environment variables.",
      hint: "Expected SUPABASE_URL and SUPABASE_SECRET_KEYS or SUPABASE_SERVICE_ROLE_KEY.",
    },
    500,
  );
}

const supabase = createClient(supabaseUrl, supabaseSecretKey);
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

  const { data, error } = await supabase.rpc(rpcName, rpcArgs);

  if (error) {
    return jsonResponse(
      {
        error: error.message,
        details: error,
      },
      500,
    );
  }

  return jsonResponse({
    query,
    mode,
    limit,
    count: data?.length ?? 0,
    results: data ?? [],
  });
});