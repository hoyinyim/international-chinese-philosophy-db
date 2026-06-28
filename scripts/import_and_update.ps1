Write-Host "STEP 1: Import incoming records..." -ForegroundColor Cyan
py scripts\import_incoming_records.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Import failed. Please check files in incoming/." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 2: Run database workflow..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File scripts\update_database.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Database workflow failed. Please fix errors before commit." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Import and update completed." -ForegroundColor Green
Write-Host "If everything looks correct, run:"
Write-Host "git add ."
Write-Host "git commit -m `"Add daily reading records`""
Write-Host "git push"