import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXPORT_DIR = ROOT / "ai_exports"


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
                record = json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"{filename} 第 {line_number} 行 JSON 格式錯誤：{e.msg}")
            if not isinstance(record, dict):
                raise RuntimeError(f"{filename} 第 {line_number} 行必須是 JSON object。")
            records.append(record)

    return records


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def as_list_text(value: Any) -> str:
    if isinstance(value, list):
        return "、".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def build_usage_corpus(usages: list[dict[str, Any]], concepts: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    lines: list[str] = []
    jsonl_records: list[dict[str, Any]] = []

    lines.append("# 國際中國哲學學術語用 AI 語料庫")
    lines.append("")
    lines.append("本檔案由 data/academic_usage.jsonl 與 data/concept_index.jsonl 自動產生。")
    lines.append("用途：供「國際中國哲學語用」AI 檢索英文學術語塊、句式、論述策略、語境、論證功能與可遷移用法。")
    lines.append("")

    if not usages:
        lines.append("目前尚無學術語用資料。")
        lines.append("")

    for record in usages:
        usage_id = record.get("usage_id", "")
        paper_id = record.get("paper_id", "")
        category = record.get("pragmatic_category", "")

        block = [
            f"## {usage_id}｜{category}",
            "",
            f"- 對應論文 ID：{paper_id}",
            f"- 作者：{record.get('author', '')}",
            f"- 論文題名：{record.get('title', '')}",
            f"- 年份：{record.get('year', '')}",
            f"- 來源：{record.get('source', '')}",
            f"- 來源位置：{record.get('source_location', '')}",
            "",
            "### 原文語句或語塊",
            record.get("original_phrase", ""),
            "",
            "### 中文語義與語境說明",
            record.get("chinese_explanation", ""),
            "",
            "### 論證功能",
            record.get("argumentative_function", ""),
            "",
            "### 值得學習之處",
            record.get("why_learnable", ""),
            "",
            "### 可遷移使用情境",
            record.get("transferable_context", ""),
            "",
            "### 可仿寫句式",
            record.get("imitable_pattern", ""),
            "",
            "### 注意事項",
            record.get("cautions", ""),
            "",
            "---",
            "",
        ]

        text = "\n".join(block)
        lines.extend(block)

        jsonl_records.append({
            "id": usage_id,
            "source_type": "academic_usage",
            "paper_id": paper_id,
            "category": category,
            "title": record.get("title", ""),
            "text": text,
            "metadata": record,
        })

    lines.append("# 概念索引補充")
    lines.append("")
    lines.append("以下概念資料用於協助 AI 進行中英概念連結、語義擴展與檢索。")
    lines.append("")

    for concept in concepts:
        lines.append(f"## {concept.get('concept_id', '')}｜{concept.get('zh_term', '')}")
        lines.append("")
        lines.append(f"- 英文術語：{as_list_text(concept.get('en_terms', []))}")
        lines.append(f"- 相關中文概念：{as_list_text(concept.get('related_zh_terms', []))}")
        lines.append(f"- 相關英文術語：{as_list_text(concept.get('related_en_terms', []))}")
        lines.append(f"- 關聯論文 ID：{as_list_text(concept.get('linked_paper_ids', []))}")
        lines.append(f"- 關聯語用 ID：{as_list_text(concept.get('linked_usage_ids', []))}")
        lines.append(f"- 補充說明：{concept.get('notes', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines), jsonl_records


def build_horizon_corpus(horizons: list[dict[str, Any]], concepts: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    lines: list[str] = []
    jsonl_records: list[dict[str, Any]] = []

    lines.append("# 國際中國哲學研究視野 AI 語料庫")
    lines.append("")
    lines.append("本檔案由 data/research_horizon.jsonl 與 data/concept_index.jsonl 自動產生。")
    lines.append("用途：供「國際中國哲學視野勘探」AI 檢索研究問題、文本材料、方法進路、學術對話對象、國際學術視野與可延伸問題。")
    lines.append("")

    if not horizons:
        lines.append("目前尚無研究視野資料。")
        lines.append("")

    for record in horizons:
        horizon_id = record.get("horizon_id", "")
        paper_id = record.get("paper_id", "")
        category = record.get("research_category", "")

        block = [
            f"## {horizon_id}｜{category}",
            "",
            f"- 對應論文 ID：{paper_id}",
            f"- 作者：{record.get('author', '')}",
            f"- 論文題名：{record.get('title', '')}",
            f"- 年份：{record.get('year', '')}",
            f"- 來源：{record.get('source', '')}",
            f"- 來源位置：{record.get('source_location', '')}",
            "",
            "### 研究主題",
            record.get("research_topic", ""),
            "",
            "### 核心研究問題",
            record.get("core_question", ""),
            "",
            "### 使用材料",
            record.get("materials", ""),
            "",
            "### 研究方法",
            record.get("method", ""),
            "",
            "### 學術對話對象",
            record.get("scholarly_interlocutors", ""),
            "",
            "### 主要論點",
            record.get("main_claim", ""),
            "",
            "### 國際學術視野",
            record.get("international_horizon", ""),
            "",
            "### 對我研究的啟發",
            record.get("relevance_to_my_research", ""),
            "",
            "### 可延伸問題",
            record.get("extendable_questions", ""),
            "",
            "---",
            "",
        ]

        text = "\n".join(block)
        lines.extend(block)

        jsonl_records.append({
            "id": horizon_id,
            "source_type": "research_horizon",
            "paper_id": paper_id,
            "category": category,
            "title": record.get("title", ""),
            "text": text,
            "metadata": record,
        })

    lines.append("# 概念索引補充")
    lines.append("")
    lines.append("以下概念資料用於協助 AI 進行研究主題擴展、材料連結與關鍵詞檢索。")
    lines.append("")

    for concept in concepts:
        lines.append(f"## {concept.get('concept_id', '')}｜{concept.get('zh_term', '')}")
        lines.append("")
        lines.append(f"- 英文術語：{as_list_text(concept.get('en_terms', []))}")
        lines.append(f"- 相關中文概念：{as_list_text(concept.get('related_zh_terms', []))}")
        lines.append(f"- 相關英文術語：{as_list_text(concept.get('related_en_terms', []))}")
        lines.append(f"- 關聯論文 ID：{as_list_text(concept.get('linked_paper_ids', []))}")
        lines.append(f"- 關聯研究視野 ID：{as_list_text(concept.get('linked_horizon_ids', []))}")
        lines.append(f"- 補充說明：{concept.get('notes', '')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines), jsonl_records


def build_usage_instructions() -> str:
    return """# GPT Instructions：國際中國哲學語用

你是「國際中國哲學語用」AI。你的任務是根據使用者輸入的中文學術意思，從「國際中國哲學學術語用資料庫」中檢索相關英文語塊、句式與論述策略，並生成可調整的英文學術句子或段落。

## 核心任務

1. 判斷使用者想表達的中文學術意思屬於哪一類語用功能。
2. 從語用資料庫中尋找相關英文語塊、句式、論述策略。
3. 回報候選英文表述。
4. 說明每一種表述的語氣、強度、適用情境與限制。
5. 根據使用者的研究主題，生成可調整的英文學術句子或段落。

## 可用語用分類

- 立場界定
- 問題提出
- 文獻定位
- 概念界定
- 論證推進
- 轉折與修正
- 反駁與批判
- 方法說明
- 材料處理
- 比較與對照
- 限制與保留
- 結論與貢獻

## 回答原則

1. 不要只做中英翻譯。
2. 必須說明英文句式的論證功能。
3. 必須說明該表述在原資料中的語境。
4. 必須說明可遷移到何種中國哲學英文寫作情境。
5. 不得虛構資料庫中沒有的來源。
6. 若資料庫不足以支持某表述，必須明確說「資料庫目前尚不足以支持」。
7. 生成英文時，應保持學術、精確、可修改，不使用誇飾語氣。

## 建議回答格式

一、語用判斷  
二、可用資料庫例句或語塊  
三、語氣與適用情境  
四、可仿寫句式  
五、依使用者主題生成英文句子  
六、注意事項
"""


def build_horizon_instructions() -> str:
    return """# GPT Instructions：國際中國哲學視野勘探

你是「國際中國哲學視野勘探」AI。你的任務是根據使用者輸入的研究主題，從「國際中國哲學研究視野資料庫」中檢索相關研究方向、材料、方法、學術對話與可延伸問題。

## 核心任務

1. 解析使用者輸入的研究主題。
2. 從研究視野資料庫中搜尋相關主題、材料、方法與概念。
3. 回報國際中國哲學學界與此主題相關的研究方向。
4. 說明目前主要研究進路、材料使用、方法特徵與學術關懷。
5. 判斷此主題還有哪些可開發空間。
6. 建議可進一步研究的材料、問題、方法與論文架構。

## 可用研究類別

- 單一哲學概念研究
- 文本詮釋與義理重構
- 思想史與概念史
- 比較哲學：中西比較
- 比較哲學：中國內部比較
- 儒家研究
- 道家研究
- 墨家、法家與諸子研究
- 經典詮釋與注疏傳統
- 出土文獻與傳世文獻對讀
- 政治哲學與倫理思想
- 修身工夫與實踐哲學
- 宗教、宇宙論與形上學
- 方法論與中國哲學合法性問題

## 回答原則

1. 不要空泛列研究方向。
2. 必須回到資料庫中的文章、材料、方法與學術對話。
3. 若資料庫不足，必須說明「目前資料庫尚不足以判定」。
4. 可以提出「可推測」的延伸方向，但必須標示為可推測。
5. 不得虛構作者、論文、頁碼、研究史或學術背景。
6. 建議研究方向時，必須說明其問題意識、材料依據與方法可能性。

## 建議回答格式

一、主題判讀  
二、資料庫中相關研究方向  
三、主要材料與方法  
四、國際學術視野  
五、可開發空間  
六、建議論文問題與架構  
七、資料不足之處
"""


def main() -> int:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    usages = read_jsonl("academic_usage.jsonl")
    horizons = read_jsonl("research_horizon.jsonl")
    concepts = read_jsonl("concept_index.jsonl")

    usage_md, usage_jsonl = build_usage_corpus(usages, concepts)
    horizon_md, horizon_jsonl = build_horizon_corpus(horizons, concepts)

    write_text(EXPORT_DIR / "academic_usage_ai_corpus.md", usage_md)
    write_text(EXPORT_DIR / "research_horizon_ai_corpus.md", horizon_md)
    write_jsonl(EXPORT_DIR / "academic_usage_ai_corpus.jsonl", usage_jsonl)
    write_jsonl(EXPORT_DIR / "research_horizon_ai_corpus.jsonl", horizon_jsonl)
    write_text(EXPORT_DIR / "usage_gpt_instructions.md", build_usage_instructions())
    write_text(EXPORT_DIR / "horizon_gpt_instructions.md", build_horizon_instructions())

    print("AI 匯出檔已建立：")
    print("- ai_exports/academic_usage_ai_corpus.md")
    print("- ai_exports/research_horizon_ai_corpus.md")
    print("- ai_exports/academic_usage_ai_corpus.jsonl")
    print("- ai_exports/research_horizon_ai_corpus.jsonl")
    print("- ai_exports/usage_gpt_instructions.md")
    print("- ai_exports/horizon_gpt_instructions.md")
    print()
    print(f"學術語用資料：{len(usages)} 筆")
    print(f"研究視野資料：{len(horizons)} 筆")
    print(f"概念索引資料：{len(concepts)} 筆")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())