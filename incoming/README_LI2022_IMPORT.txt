LI2022 incoming 匯入包

使用方式：
1. 將本壓縮檔內四個 *_append.jsonl 檔案解壓到專案的 incoming/ 資料夾。
2. 回到專案根目錄，執行：
   powershell -ExecutionPolicy Bypass -File scripts\import_and_update.ps1
3. 若流程通過，再執行：
   git status
   git add .
   git commit -m "Add Li 2022 reading records"
   git push

本包內容：
- papers_append.jsonl：1 筆
- academic_usage_append.jsonl：16 筆
- research_horizon_append.jsonl：1 筆
- concept_index_append.jsonl：10 筆

注意：
- 語用資料中原本的多重分類已轉為目前 schema 可接受的主分類；原分類保留在 cautions 欄位末尾。
- 研究視野資料的主分類暫定為「儒家研究」；其他分類保留在 paper metadata 的 research_area 中。
