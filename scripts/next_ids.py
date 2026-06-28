import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


FILES = {
    "paper": ("papers.jsonl", "paper_id", "P"),
    "usage": ("academic_usage.jsonl", "usage_id", "U"),
    "horizon": ("research_horizon.jsonl", "horizon_id", "H"),
}


def read_jsonl(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    records: list[dict[str, Any]] = []

    if not path.exists():
        return records

    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            text = line.strip()
            if not text:
                continue
            records.append(json.loads(text))

    return records


def next_id(prefix: str, ids: list[str], yyyymmdd: str) -> str:
    pattern = re.compile(rf"^{prefix}{yyyymmdd}-(\d+)$")
    numbers: list[int] = []

    for value in ids:
        match = pattern.match(value)
        if match:
            numbers.append(int(match.group(1)))

    next_number = max(numbers, default=0) + 1
    return f"{prefix}{yyyymmdd}-{next_number:03d}"


def next_concept_id() -> str:
    records = read_jsonl("concept_index.jsonl")
    pattern = re.compile(r"^C(\d+)$")
    numbers: list[int] = []

    for record in records:
        value = record.get("concept_id", "")
        match = pattern.match(value)
        if match:
            numbers.append(int(match.group(1)))

    next_number = max(numbers, default=0) + 1
    return f"C{next_number:04d}"


def main() -> int:
    today = date.today()
    yyyy_mm_dd = today.isoformat()
    yyyymmdd = today.strftime("%Y%m%d")

    paper_records = read_jsonl("papers.jsonl")
    usage_records = read_jsonl("academic_usage.jsonl")
    horizon_records = read_jsonl("research_horizon.jsonl")

    paper_id = next_id("P", [r.get("paper_id", "") for r in paper_records], yyyymmdd)
    usage_id = next_id("U", [r.get("usage_id", "") for r in usage_records], yyyymmdd)
    horizon_id = next_id("H", [r.get("horizon_id", "") for r in horizon_records], yyyymmdd)
    concept_id = next_concept_id()

    print("下一組建議 ID")
    print("==============================")
    print(f"整理日期：{yyyy_mm_dd}")
    print(f"paper_id：{paper_id}")
    print(f"usage_id：{usage_id}")
    print(f"horizon_id：{horizon_id}")
    print(f"concept_id：{concept_id}")
    print()

    print("論文基本資料範本")
    print("==============================")
    print(
        f'{{"paper_id":"{paper_id}","date":"{yyyy_mm_dd}","author":"","title":"","year":"","journal":"","doi":"","research_area":[],"keywords_en":[],"keywords_zh":[],"notes":""}}'
    )
    print()

    print("學術語用資料範本")
    print("==============================")
    print(
        f'{{"usage_id":"{usage_id}","paper_id":"{paper_id}","date":"{yyyy_mm_dd}","author":"","title":"","year":"","source":"","original_phrase":"","pragmatic_category":"","chinese_explanation":"","argumentative_function":"","why_learnable":"","transferable_context":"","imitable_pattern":"","cautions":"","source_location":""}}'
    )
    print()

    print("研究視野資料範本")
    print("==============================")
    print(
        f'{{"horizon_id":"{horizon_id}","paper_id":"{paper_id}","date":"{yyyy_mm_dd}","author":"","title":"","year":"","source":"","research_topic":"","research_category":"","core_question":"","materials":"","method":"","scholarly_interlocutors":"","main_claim":"","international_horizon":"","relevance_to_my_research":"","extendable_questions":"","source_location":""}}'
    )
    print()

    print("概念索引資料範本")
    print("==============================")
    print(
        f'{{"concept_id":"{concept_id}","zh_term":"","en_terms":[],"related_zh_terms":[],"related_en_terms":[],"linked_paper_ids":["{paper_id}"],"linked_usage_ids":["{usage_id}"],"linked_horizon_ids":["{horizon_id}"],"notes":""}}'
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())