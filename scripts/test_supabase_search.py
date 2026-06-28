import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("缺少 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY。請檢查 .env。")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def search(function_name: str, query: str, limit: int = 5) -> None:
    print()
    print("=" * 60)
    print(f"{function_name}｜query = {query}")
    print("=" * 60)

    response = supabase.rpc(
        function_name,
        {
            "query_text": query,
            "limit_count": limit,
        },
    ).execute()

    rows = response.data or []

    if not rows:
        print("沒有找到資料。")
        return

    for index, row in enumerate(rows, start=1):
        print(f"{index}. [{row.get('source_type')}] {row.get('source_id')}")
        print(f"   題名：{row.get('title')}")
        print(f"   作者：{row.get('author')}")
        print(f"   分類：{row.get('category')}")
        print(f"   score：{row.get('score')}")
        content = row.get("content", "").replace("\n", " ")
        print(f"   摘要：{content[:160]}...")
        print()


def main() -> int:
    search("search_chunks_keyword", "勞思光")
    search("search_usage_keyword", "Far from")
    search("search_horizon_keyword", "儒家")
    search("search_concepts_keyword", "天地")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
