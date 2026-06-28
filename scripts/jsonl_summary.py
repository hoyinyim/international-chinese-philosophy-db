import json
from pathlib import Path
from collections import Counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


FILES = {
    "論文基本資料": "papers.jsonl",
    "學術語用資料": "academic_usage.jsonl",
    "研究視野資料": "research_horizon.jsonl",
    "概念索引資料": "concept_index.jsonl",
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


def print_basic_counts(all_data: dict[str, list[dict[str, Any]]]) -> None:
    print("資料庫目前累積狀況")
    print("=" * 30)

    for label, records in all_data.items():
        print(f"{label}：{len(records)} 筆")

    print()


def print_paper_summary(papers: list[dict[str, Any]]) -> None:
    if not papers:
        print("尚無論文基本資料。")
        print()
        return

    print("論文清單")
    print("=" * 30)

    for paper in papers:
        paper_id = paper.get("paper_id", "")
        author = paper.get("author", "")
        year = paper.get("year", "")
        title = paper.get("title", "")
        journal = paper.get("journal", "")

        print(f"- {paper_id}｜{author}｜{year}｜{title}｜{journal}")

    print()


def print_usage_categories(usages: list[dict[str, Any]]) -> None:
    if not usages:
        print("尚無學術語用分類資料。")
        print()
        return

    counter = Counter(record.get("pragmatic_category", "未分類") for record in usages)

    print("學術語用分類統計")
    print("=" * 30)

    for category, count in counter.most_common():
        print(f"- {category}：{count} 筆")

    print()


def print_research_categories(horizons: list[dict[str, Any]]) -> None:
    if not horizons:
        print("尚無研究類別資料。")
        print()
        return

    counter = Counter(record.get("research_category", "未分類") for record in horizons)

    print("研究類別統計")
    print("=" * 30)

    for category, count in counter.most_common():
        print(f"- {category}：{count} 筆")

    print()


def print_concepts(concepts: list[dict[str, Any]]) -> None:
    if not concepts:
        print("尚無概念索引資料。")
        print()
        return

    print("概念索引")
    print("=" * 30)

    for concept in concepts:
        concept_id = concept.get("concept_id", "")
        zh_term = concept.get("zh_term", "")
        en_terms = ", ".join(concept.get("en_terms", []))

        print(f"- {concept_id}｜{zh_term}｜{en_terms}")

    print()


def main() -> int:
    all_data = {
        label: read_jsonl(filename)
        for label, filename in FILES.items()
    }

    print_basic_counts(all_data)
    print_paper_summary(all_data["論文基本資料"])
    print_usage_categories(all_data["學術語用資料"])
    print_research_categories(all_data["研究視野資料"])
    print_concepts(all_data["概念索引資料"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())