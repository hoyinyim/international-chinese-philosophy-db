import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


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


def check_duplicate_ids(
    records: list[dict[str, Any]],
    id_field: str,
    label: str,
    errors: list[str],
) -> set[str]:
    seen: set[str] = set()
    duplicated: set[str] = set()

    for record in records:
        value = record.get(id_field)

        if not isinstance(value, str) or not value:
            errors.append(f"{label} 有資料缺少 {id_field}。")
            continue

        if value in seen:
            duplicated.add(value)
        else:
            seen.add(value)

    for value in sorted(duplicated):
        errors.append(f"{label} 的 {id_field} 重複：{value}")

    return seen


def check_array_links(
    record: dict[str, Any],
    field_name: str,
    valid_ids: set[str],
    label: str,
    record_id: str,
    errors: list[str],
) -> None:
    values = record.get(field_name, [])

    if values is None:
        values = []

    if not isinstance(values, list):
        errors.append(f"{label} {record_id} 的 {field_name} 必須是陣列。")
        return

    for value in values:
        if value not in valid_ids:
            errors.append(f"{label} {record_id} 的 {field_name} 連到不存在的 ID：{value}")


def main() -> int:
    errors: list[str] = []

    papers = read_jsonl("papers.jsonl")
    usage = read_jsonl("academic_usage.jsonl")
    horizon = read_jsonl("research_horizon.jsonl")
    concepts = read_jsonl("concept_index.jsonl")

    paper_ids = check_duplicate_ids(papers, "paper_id", "papers.jsonl", errors)
    usage_ids = check_duplicate_ids(usage, "usage_id", "academic_usage.jsonl", errors)
    horizon_ids = check_duplicate_ids(horizon, "horizon_id", "research_horizon.jsonl", errors)
    concept_ids = check_duplicate_ids(concepts, "concept_id", "concept_index.jsonl", errors)

    for record in usage:
      usage_id = record.get("usage_id", "UNKNOWN")
      paper_id = record.get("paper_id")

      if paper_id not in paper_ids:
          errors.append(f"academic_usage.jsonl {usage_id} 連到不存在的 paper_id：{paper_id}")

    for record in horizon:
      horizon_id = record.get("horizon_id", "UNKNOWN")
      paper_id = record.get("paper_id")

      if paper_id not in paper_ids:
          errors.append(f"research_horizon.jsonl {horizon_id} 連到不存在的 paper_id：{paper_id}")

    for record in concepts:
        concept_id = record.get("concept_id", "UNKNOWN")

        check_array_links(
            record,
            "linked_paper_ids",
            paper_ids,
            "concept_index.jsonl",
            concept_id,
            errors,
        )

        check_array_links(
            record,
            "linked_usage_ids",
            usage_ids,
            "concept_index.jsonl",
            concept_id,
            errors,
        )

        check_array_links(
            record,
            "linked_horizon_ids",
            horizon_ids,
            "concept_index.jsonl",
            concept_id,
            errors,
        )

    if errors:
        print("資料關聯檢查未通過。")
        print()
        for error in errors:
            print(f"- {error}")
        return 1

    print("資料關聯檢查通過。")
    print(f"- 論文 ID：{len(paper_ids)} 筆")
    print(f"- 語用 ID：{len(usage_ids)} 筆")
    print(f"- 研究視野 ID：{len(horizon_ids)} 筆")
    print(f"- 概念 ID：{len(concept_ids)} 筆")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())