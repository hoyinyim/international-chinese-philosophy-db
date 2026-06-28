# 每日國際中國哲學期刊資料輸入範本

本範本用於每日閱讀中國哲學、國際漢學、比較哲學與東亞思想研究英文期刊論文後，將資料轉入本專案的 JSONL 資料庫。每一筆 JSON 必須維持單行，不可換行。

---

## 一、論文基本資料

存入檔案：

```text
data/papers.jsonl
```

範本：

```json
{"paper_id":"PYYYYMMDD-001","date":"YYYY-MM-DD","author":"","title":"","year":"","journal":"","doi":"","research_area":[],"keywords_en":[],"keywords_zh":[],"notes":""}
```

填寫說明：

```text
paper_id：論文唯一 ID，例如 P20260628-001。
date：整理日期。
author：論文作者。
title：論文題名。
year：論文出版年份。
journal：期刊或書籍來源。
doi：DOI 或穩定連結；沒有則留空字串。
research_area：研究領域，可填多項。
keywords_en：英文關鍵詞。
keywords_zh：中文關鍵詞。
notes：補充說明。
```

---

## 二、學術語用資料

存入檔案：

```text
data/academic_usage.jsonl
```

範本：

```json
{"usage_id":"UYYYYMMDD-001","paper_id":"PYYYYMMDD-001","date":"YYYY-MM-DD","author":"","title":"","year":"","source":"","original_phrase":"","pragmatic_category":"","chinese_explanation":"","argumentative_function":"","why_learnable":"","transferable_context":"","imitable_pattern":"","cautions":"","source_location":""}
```

可用語用分類：

```text
立場界定
問題提出
文獻定位
概念界定
論證推進
轉折與修正
反駁與批判
方法說明
材料處理
比較與對照
限制與保留
結論與貢獻
```

填寫說明：

```text
usage_id：語用資料唯一 ID，例如 U20260628-001。
paper_id：連結到 papers.jsonl 的 paper_id。
original_phrase：英文原文語句或語塊，避免大段複製。
pragmatic_category：必須使用上方固定分類。
chinese_explanation：中文語義與語用說明。
argumentative_function：此語句在論文中的論證功能。
why_learnable：此用法值得學習的原因。
transferable_context：可遷移到何種中國哲學英文寫作情境。
imitable_pattern：可仿寫句式。
cautions：語氣強弱、適用限制、不可誤用之處。
source_location：頁碼、章節、段落位置；若無頁碼，須說明。
```

---

## 三、研究視野資料

存入檔案：

```text
data/research_horizon.jsonl
```

範本：

```json
{"horizon_id":"HYYYYMMDD-001","paper_id":"PYYYYMMDD-001","date":"YYYY-MM-DD","author":"","title":"","year":"","source":"","research_topic":"","research_category":"","core_question":"","materials":"","method":"","scholarly_interlocutors":"","main_claim":"","international_horizon":"","relevance_to_my_research":"","extendable_questions":"","source_location":""}
```

可用研究類別：

```text
單一哲學概念研究
文本詮釋與義理重構
思想史與概念史
比較哲學：中西比較
比較哲學：中國內部比較
儒家研究
道家研究
墨家、法家與諸子研究
經典詮釋與注疏傳統
出土文獻與傳世文獻對讀
政治哲學與倫理思想
修身工夫與實踐哲學
宗教、宇宙論與形上學
方法論與中國哲學合法性問題
```

填寫說明：

```text
horizon_id：研究視野資料唯一 ID，例如 H20260628-001。
paper_id：連結到 papers.jsonl 的 paper_id。
research_topic：研究主題。
research_category：必須使用上方固定分類。
core_question：核心研究問題。
materials：作者使用的文本、材料或案例。
method：研究方法與進路。
scholarly_interlocutors：作者回應的學術問題、學者或研究傳統。
main_claim：主要論點。
international_horizon：此文反映的國際學術視野。
relevance_to_my_research：對我未來研究的啟發。
extendable_questions：可延伸的研究問題。
source_location：頁碼、章節、段落位置；若無頁碼，須說明。
```

---

## 四、概念索引資料

存入檔案：

```text
data/concept_index.jsonl
```

範本：

```json
{"concept_id":"C0001","zh_term":"","en_terms":[],"related_zh_terms":[],"related_en_terms":[],"linked_paper_ids":[],"linked_usage_ids":[],"linked_horizon_ids":[],"notes":""}
```

填寫說明：

```text
concept_id：概念唯一 ID，例如 C0001。
zh_term：中文概念，例如「工夫」「仁」「義」「天」「心」。
en_terms：英文對應詞，可填多項。
related_zh_terms：相關中文概念。
related_en_terms：相關英文術語。
linked_paper_ids：相關論文 ID。
linked_usage_ids：相關語用資料 ID。
linked_horizon_ids：相關研究視野資料 ID。
notes：補充說明。
```

---

## 五、每日更新流程

新增資料後，先執行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\update_database.ps1
```

若資料驗證通過，再執行：

```powershell
git add .
git commit -m "Add daily reading records"
git push
```

---

## 六、資料輸入注意事項

```text
1. 每一筆 JSONL 必須是一行完整 JSON，不可換行。
2. 字串必須使用英文雙引號。
3. 陣列欄位必須使用 []，不可寫成一般文字。
4. 分類欄位必須使用固定分類，不可自行新增近似名稱。
5. 若資料不足，必須寫「尚不足以判定」或「可推測」，不得斷言。
6. 不得大量複製受版權保護論文原文。
7. 原文語句應以短語、句型或關鍵句為主。
8. 每筆資料必須能回溯到具體論文與來源位置。
```
