import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import create_client


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

load_dotenv(ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("缺少 SUPABASE_URL 或 SUPABASE_SERVICE_ROLE_KEY。請檢查 .env。")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def read_jsonl(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    records: list[dict[str, Any]] = []

    if not path.exists():
        return records

    with path.open("r", encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue

            try:
                obj = json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"{filename} 第 {line_number} 行 JSON 錯誤：{e.msg}")

            if not isinstance(obj, dict):
                raise RuntimeError(f"{filename} 第 {line_number} 行不是 JSON object。")

            records.append(obj)

    return records


def batch_upsert(table: str, records: list[dict[str, Any]], conflict_key: str) -> None:
    if not records:
        print(f"[NONE] {table}：0 筆")
        return

    batch_size = 100

    for start in range(0, len(records), batch_size):
        batch = records[start : start + batch_size]
        response = supabase.table(table).upsert(batch, on_conflict=conflict_key).execute()

        if getattr(response, "data", None) is None:
            raise RuntimeError(f"{table} upsert 可能失敗，請檢查 Supabase 回應。")

    print(f"[OK] {table}：同步 {len(records)} 筆")


def as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value if v is not None and str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def make_paper_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": record["paper_id"],
        "date": record["date"],
        "author": record["author"],
        "title": record["title"],
        "year": record["year"],
        "journal": record["journal"],
        "doi": record.get("doi", ""),
        "research_area": as_text_list(record.get("research_area", [])),
        "keywords_en": as_text_list(record.get("keywords_en", [])),
        "keywords_zh": as_text_list(record.get("keywords_zh", [])),
        "notes": record.get("notes", ""),
        "raw": record,
    }


def make_usage_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "usage_id": record["usage_id"],
        "paper_id": record["paper_id"],
        "date": record["date"],
        "author": record["author"],
        "title": record["title"],
        "year": record["year"],
        "source": record["source"],
        "original_phrase": record["original_phrase"],
        "pragmatic_category": record["pragmatic_category"],
        "chinese_explanation": record["chinese_explanation"],
        "argumentative_function": record["argumentative_function"],
        "why_learnable": record["why_learnable"],
        "transferable_context": record["transferable_context"],
        "imitable_pattern": record["imitable_pattern"],
        "cautions": record["cautions"],
        "source_location": record.get("source_location", ""),
        "raw": record,
    }


def make_horizon_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "horizon_id": record["horizon_id"],
        "paper_id": record["paper_id"],
        "date": record["date"],
        "author": record["author"],
        "title": record["title"],
        "year": record["year"],
        "source": record["source"],
        "research_topic": record["research_topic"],
        "research_category": record["research_category"],
        "core_question": record["core_question"],
        "materials": record["materials"],
        "method": record["method"],
        "scholarly_interlocutors": record["scholarly_interlocutors"],
        "main_claim": record["main_claim"],
        "international_horizon": record["international_horizon"],
        "relevance_to_my_research": record["relevance_to_my_research"],
        "extendable_questions": record["extendable_questions"],
        "source_location": record.get("source_location", ""),
        "raw": record,
    }


def make_concept_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "concept_id": record["concept_id"],
        "zh_term": record["zh_term"],
        "en_terms": as_text_list(record.get("en_terms", [])),
        "related_zh_terms": as_text_list(record.get("related_zh_terms", [])),
        "related_en_terms": as_text_list(record.get("related_en_terms", [])),
        "linked_paper_ids": as_text_list(record.get("linked_paper_ids", [])),
        "linked_usage_ids": as_text_list(record.get("linked_usage_ids", [])),
        "linked_horizon_ids": as_text_list(record.get("linked_horizon_ids", [])),
        "notes": record.get("notes", ""),
        "raw": record,
    }


def build_chunks(
    papers: list[dict[str, Any]],
    usage: list[dict[str, Any]],
    horizons: list[dict[str, Any]],
    concepts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for r in papers:
        content = "\n".join(
            [
                f"論文：{r.get('title', '')}",
                f"作者：{r.get('author', '')}",
                f"年份：{r.get('year', '')}",
                f"來源：{r.get('journal', '')}",
                f"研究領域：{'、'.join(as_text_list(r.get('research_area', [])))}",
                f"英文關鍵詞：{'、'.join(as_text_list(r.get('keywords_en', [])))}",
                f"中文關鍵詞：{'、'.join(as_text_list(r.get('keywords_zh', [])))}",
                f"說明：{r.get('notes', '')}",
            ]
        )

        chunks.append(
            {
                "chunk_id": f"paper__{r['paper_id']}",
                "source_type": "paper",
                "source_id": r["paper_id"],
                "paper_id": r["paper_id"],
                "title": r.get("title", ""),
                "author": r.get("author", ""),
                "category": "",
                "concepts": as_text_list(r.get("keywords_zh", [])) + as_text_list(r.get("keywords_en", [])),
                "content": content,
                "metadata": r,
            }
        )

    for r in usage:
        content = "\n".join(
            [
                f"語用分類：{r.get('pragmatic_category', '')}",
                f"原文語句：{r.get('original_phrase', '')}",
                f"中文說明：{r.get('chinese_explanation', '')}",
                f"論證功能：{r.get('argumentative_function', '')}",
                f"值得學習之處：{r.get('why_learnable', '')}",
                f"可遷移使用情境：{r.get('transferable_context', '')}",
                f"可仿寫句式：{r.get('imitable_pattern', '')}",
                f"注意事項：{r.get('cautions', '')}",
                f"論文：{r.get('title', '')}",
                f"作者：{r.get('author', '')}",
            ]
        )

        chunks.append(
            {
                "chunk_id": f"academic_usage__{r['usage_id']}",
                "source_type": "academic_usage",
                "source_id": r["usage_id"],
                "paper_id": r["paper_id"],
                "title": r.get("title", ""),
                "author": r.get("author", ""),
                "category": r.get("pragmatic_category", ""),
                "concepts": [],
                "content": content,
                "metadata": r,
            }
        )

    for r in horizons:
        content = "\n".join(
            [
                f"研究主題：{r.get('research_topic', '')}",
                f"研究類別：{r.get('research_category', '')}",
                f"核心問題：{r.get('core_question', '')}",
                f"使用材料：{r.get('materials', '')}",
                f"研究方法：{r.get('method', '')}",
                f"學術對話對象：{r.get('scholarly_interlocutors', '')}",
                f"主要論點：{r.get('main_claim', '')}",
                f"國際學術視野：{r.get('international_horizon', '')}",
                f"對我研究的啟發：{r.get('relevance_to_my_research', '')}",
                f"可延伸問題：{r.get('extendable_questions', '')}",
                f"論文：{r.get('title', '')}",
                f"作者：{r.get('author', '')}",
            ]
        )

        chunks.append(
            {
                "chunk_id": f"research_horizon__{r['horizon_id']}",
                "source_type": "research_horizon",
                "source_id": r["horizon_id"],
                "paper_id": r["paper_id"],
                "title": r.get("title", ""),
                "author": r.get("author", ""),
                "category": r.get("research_category", ""),
                "concepts": [],
                "content": content,
                "metadata": r,
            }
        )

    for r in concepts:
        linked_papers = as_text_list(r.get("linked_paper_ids", []))
        content = "\n".join(
            [
                f"中文概念：{r.get('zh_term', '')}",
                f"英文術語：{'、'.join(as_text_list(r.get('en_terms', [])))}",
                f"相關中文概念：{'、'.join(as_text_list(r.get('related_zh_terms', [])))}",
                f"相關英文術語：{'、'.join(as_text_list(r.get('related_en_terms', [])))}",
                f"說明：{r.get('notes', '')}",
            ]
        )

        chunks.append(
            {
                "chunk_id": f"concept__{r['concept_id']}",
                "source_type": "concept",
                "source_id": r["concept_id"],
                "paper_id": linked_papers[0] if linked_papers else None,
                "title": "",
                "author": "",
                "category": "concept",
                "concepts": [r.get("zh_term", "")]
                + as_text_list(r.get("en_terms", []))
                + as_text_list(r.get("related_zh_terms", []))
                + as_text_list(r.get("related_en_terms", [])),
                "content": content,
                "metadata": r,
            }
        )

    return chunks


def main() -> int:
    papers_raw = read_jsonl("papers.jsonl")
    usage_raw = read_jsonl("academic_usage.jsonl")
    horizons_raw = read_jsonl("research_horizon.jsonl")
    concepts_raw = read_jsonl("concept_index.jsonl")

    papers = [make_paper_row(r) for r in papers_raw]
    usage = [make_usage_row(r) for r in usage_raw]
    horizons = [make_horizon_row(r) for r in horizons_raw]
    concepts = [make_concept_row(r) for r in concepts_raw]

    print("開始同步資料到 Supabase。")
    print()

    batch_upsert("papers", papers, "paper_id")
    batch_upsert("academic_usage", usage, "usage_id")
    batch_upsert("research_horizon", horizons, "horizon_id")
    batch_upsert("concept_index", concepts, "concept_id")

    chunks = build_chunks(papers_raw, usage_raw, horizons_raw, concepts_raw)
    batch_upsert("retrieval_chunks", chunks, "chunk_id")

    print()
    print("Supabase 同步完成。")
    print(f"- papers：{len(papers)}")
    print(f"- academic_usage：{len(usage)}")
    print(f"- research_horizon：{len(horizons)}")
    print(f"- concept_index：{len(concepts)}")
    print(f"- retrieval_chunks：{len(chunks)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())