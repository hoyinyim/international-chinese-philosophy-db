import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
INCOMING_DIR = ROOT / "incoming"


IMPORT_MAP = {
    "papers_append.jsonl": ("papers.jsonl", "paper_id"),
    "academic_usage_append.jsonl": ("academic_usage.jsonl", "usage_id"),
    "research_horizon_append.jsonl": ("research_horizon.jsonl", "horizon_id"),
    "concept_index_append.jsonl": ("concept_index.jsonl", "concept_id"),
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
                raise RuntimeError(f"{path} 第 {line_number} 行 JSON 格式錯誤：{e.msg}")

            if not isinstance(obj, dict):
                raise RuntimeError(f"{path} 第 {line_number} 行必須是一個 JSON object。")

            records.append(obj)

    return records


def append_unique_records(
    incoming_path: Path,
    target_path: Path,
    id_field: str,
) -> int:
    existing_records = read_jsonl(target_path)
    incoming_records = read_jsonl(incoming_path)

    existing_ids = {
        record.get(id_field)
        for record in existing_records
        if isinstance(record.get(id_field), str)
    }

    new_records: list[dict[str, Any]] = []

    for record in incoming_records:
        record_id = record.get(id_field)

        if not isinstance(record_id, str) or not record_id:
            raise RuntimeError(f"{incoming_path.name} 有資料缺少 {id_field}。")

        if record_id in existing_ids:
            print(f"[SKIP] {record_id} 已存在，略過。")
            continue

        new_records.append(record)
        existing_ids.add(record_id)

    if not new_records:
        return 0

    target_path.parent.mkdir(parents=True, exist_ok=True)

    with target_path.open("a", encoding="utf-8") as f:
        for record in new_records:
            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")

    return len(new_records)


def main() -> int:
    if not INCOMING_DIR.exists():
        print("incoming/ 不存在，未匯入任何資料。")
        return 0

    total = 0

    for incoming_filename, (target_filename, id_field) in IMPORT_MAP.items():
        incoming_path = INCOMING_DIR / incoming_filename
        target_path = DATA_DIR / target_filename

        if not incoming_path.exists():
            print(f"[NONE] {incoming_filename} 不存在，略過。")
            continue

        count = append_unique_records(incoming_path, target_path, id_field)
        total += count
        print(f"[OK] {incoming_filename} → {target_filename}：新增 {count} 筆。")

    print()
    print(f"匯入完成：共新增 {total} 筆資料。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())