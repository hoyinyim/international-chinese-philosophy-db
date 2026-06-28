Write-Host "STEP 1: Validate JSONL schema..." -ForegroundColor Cyan
py scripts\validate_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Schema validation failed. Please fix JSONL files in data/ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 2: Check data integrity..." -ForegroundColor Cyan
py scripts\check_integrity.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Data integrity check failed. Please fix broken IDs or links first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 3: Build website data..." -ForegroundColor Cyan
py scripts\build_site_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Website data build failed. Please check build_site_data.py or data/ files." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 4: Show database summary..." -ForegroundColor Cyan
py scripts\jsonl_summary.py

Write-Host ""
Write-Host "STEP 5: Show Git status..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "Workflow completed." -ForegroundColor Green
Write-Host "If there are changes, run:"
Write-Host "git add ."
Write-Host "git commit -m `"Update database records`""
Write-Host "git push"