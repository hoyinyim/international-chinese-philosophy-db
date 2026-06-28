Write-Host "開始檢查資料庫格式..." -ForegroundColor Cyan
py scripts\validate_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "資料驗證失敗。請先修正 data/ 內的 JSONL 檔案。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "開始生成網站資料..." -ForegroundColor Cyan
py scripts\build_site_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "網站資料生成失敗。請檢查 build_site_data.py 或 data/ 內容。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "顯示資料庫目前摘要..." -ForegroundColor Cyan
py scripts\jsonl_summary.py

Write-Host ""
Write-Host "顯示 Git 狀態..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "更新流程完成。若有變更，請執行：" -ForegroundColor Green
Write-Host "git add ."
Write-Host "git commit -m `"Update database records`""
Write-Host "git push"