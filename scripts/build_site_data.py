import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DATA_DIR = ROOT / "docs" / "data"


SOURCE_FILES = {
    "papers": "papers.jsonl",
    "academic_usage": "academic_usage.jsonl",
    "research_horizon": "research_horizon.jsonl",
    "concept_index": "concept_index.jsonl",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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
                raise RuntimeError(
                    f"{path} 第 {line_number} 行 JSON 格式錯誤：{e.msg}"
                )
            if not isinstance(obj, dict):
                raise RuntimeError(
                    f"{path} 第 {line_number} 行必須是一個 JSON object。"
                )
            records.append(obj)

    return records


def main() -> int:
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    site_data: dict[str, list[dict[str, Any]]] = {}

    for key, filename in SOURCE_FILES.items():
        site_data[key] = read_jsonl(DATA_DIR / filename)

    summary = {
        "papers_count": len(site_data["papers"]),
        "academic_usage_count": len(site_data["academic_usage"]),
        "research_horizon_count": len(site_data["research_horizon"]),
        "concept_index_count": len(site_data["concept_index"]),
    }

    site_data_path = DOCS_DATA_DIR / "site_data.json"
    summary_path = DOCS_DATA_DIR / "site_summary.json"

    with site_data_path.open("w", encoding="utf-8") as f:
        json.dump(site_data, f, ensure_ascii=False, indent=2)

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("已建立網站資料：")
    print(f"- {site_data_path}")
    print(f"- {summary_path}")
    print()
    print("資料統計：")
    print(f"- 論文基本資料：{summary['papers_count']} 筆")
    print(f"- 學術語用資料：{summary['academic_usage_count']} 筆")
    print(f"- 研究視野資料：{summary['research_horizon_count']} 筆")
    print(f"- 概念索引資料：{summary['concept_index_count']} 筆")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())