import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DATA_SCHEMA_MAP = {
    "papers.jsonl": "papers.schema.json",
    "academic_usage.jsonl": "academic_usage.schema.json",
    "research_horizon.jsonl": "research_horizon.schema.json",
    "concept_index.jsonl": "concept_index.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    """讀取 JSON 檔案。"""
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"找不到檔案：{path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 格式錯誤：{path}，第 {e.lineno} 行，第 {e.colno} 欄：{e.msg}")


def load_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    """讀取 JSONL 檔案。每一行必須是一筆 JSON object。空行會略過。"""
    records: list[tuple[int, dict[str, Any]]] = []

    if not path.exists():
        raise RuntimeError(f"找不到資料檔：{path}")

    with path.open("r", encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            text = line.strip()

            if not text:
                continue

            try:
                obj = json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"{path} 第 {line_number} 行不是合法 JSON：第 {e.colno} 欄：{e.msg}"
                )

            if not isinstance(obj, dict):
                raise RuntimeError(
                    f"{path} 第 {line_number} 行必須是一個 JSON object。"
                )

            records.append((line_number, obj))

    return records


def check_type(value: Any, expected_type: str) -> bool:
    """依據 JSON Schema 的基本 type 檢查資料型態。"""
    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "array":
        return isinstance(value, list)

    if expected_type == "object":
        return isinstance(value, dict)

    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type == "boolean":
        return isinstance(value, bool)

    return True


def validate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    data_file: str,
    line_number: int,
) -> list[str]:
    """檢查單筆資料是否符合 schema。"""
    errors: list[str] = []

    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    allow_extra = schema.get("additionalProperties", True)

    for field in required_fields:
        if field not in record:
            errors.append(f"{data_file} 第 {line_number} 行缺少必要欄位：{field}")

    if allow_extra is False:
        allowed_fields = set(properties.keys())
        for field in record.keys():
            if field not in allowed_fields:
                errors.append(f"{data_file} 第 {line_number} 行出現未定義欄位：{field}")

    for field, value in record.items():
        if field not in properties:
            continue

        rule = properties[field]

        expected_type = rule.get("type")
        if expected_type and not check_type(value, expected_type):
            errors.append(
                f"{data_file} 第 {line_number} 行欄位 {field} 型態錯誤："
                f"預期 {expected_type}，實際為 {type(value).__name__}"
            )

        if expected_type == "array":
            item_rule = rule.get("items", {})
            item_type = item_rule.get("type")

            if item_type:
                for index, item in enumerate(value):
                    if not check_type(item, item_type):
                        errors.append(
                            f"{data_file} 第 {line_number} 行欄位 {field} "
                            f"第 {index + 1} 個元素型態錯誤：預期 {item_type}，"
                            f"實際為 {type(item).__name__}"
                        )

        enum_values = rule.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{data_file} 第 {line_number} 行欄位 {field} 不在允許分類中：{value}"
            )

    return errors


def validate_file(data_filename: str, schema_filename: str) -> list[str]:
    """檢查單一 JSONL 資料檔。"""
    data_path = ROOT / "data" / data_filename
    schema_path = ROOT / "schema" / schema_filename

    schema = load_json(schema_path)
    records = load_jsonl(data_path)

    errors: list[str] = []

    for line_number, record in records:
        errors.extend(validate_record(record, schema, data_filename, line_number))

    if not records:
        print(f"[OK] {data_filename}：目前沒有資料。")
    else:
        print(f"[OK] {data_filename}：已檢查 {len(records)} 筆資料。")

    return errors


def main() -> int:
    print("開始檢查 data/ 內的 JSONL 資料。")
    print()

    all_errors: list[str] = []

    for data_filename, schema_filename in DATA_SCHEMA_MAP.items():
        try:
            errors = validate_file(data_filename, schema_filename)
            all_errors.extend(errors)
        except RuntimeError as e:
            all_errors.append(str(e))

    print()

    if all_errors:
        print("資料檢查未通過。")
        print()
        for error in all_errors:
            print(f"- {error}")
        return 1

    print("資料檢查通過。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())