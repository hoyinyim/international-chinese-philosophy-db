[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
}

function Write-Check {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [bool]$Ok,

        [string]$Detail = ""
    )

    if ($Ok) {
        Write-Host "[OK] $Name" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] $Name" -ForegroundColor Yellow
    }

    if ($Detail) {
        Write-Host "     $Detail"
    }
}

function Get-JsonlLineCount {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $count = 0

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    foreach ($line in [System.IO.File]::ReadLines($Path, [System.Text.Encoding]::UTF8)) {
        if (-not [string]::IsNullOrWhiteSpace($line)) {
            $count += 1
        }
    }

    return $count
}

Set-Location -LiteralPath $RepoRoot

Write-Host "ICPDB daily update health check"
Write-Host "Repository: $RepoRoot"
Write-Host "Checked at: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"

Write-Section "Core Files"

$envPath = Join-Path $RepoRoot ".env"
Write-Check -Name ".env exists" -Ok (Test-Path -LiteralPath $envPath -PathType Leaf) -Detail "Only existence is checked; content is not read."

$dailyUpdatePath = Join-Path $RepoRoot "scripts\daily_update.ps1"
Write-Check -Name "scripts/daily_update.ps1 exists" -Ok (Test-Path -LiteralPath $dailyUpdatePath -PathType Leaf)

Write-Section "Python Launcher"

$pyCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pyCommand) {
    $pyVersionOutput = @(& py -3 --version 2>&1)
    $pyExitCode = $LASTEXITCODE
    Write-Check -Name "py -3 is available" -Ok ($pyExitCode -eq 0) -Detail (($pyVersionOutput | Out-String).Trim())
}
else {
    Write-Check -Name "py command exists" -Ok $false -Detail "Python Launcher was not found in PATH."
}

Write-Section "Scheduled Task"

$taskName = "ICPDB Daily Update"
$scheduledTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($scheduledTask) {
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
    Write-Check -Name "Scheduled Task exists" -Ok $true -Detail $taskName

    if ($taskInfo) {
        Write-Host ("NextRunTime: {0}" -f $taskInfo.NextRunTime)
        Write-Host ("LastRunTime: {0}" -f $taskInfo.LastRunTime)
        Write-Host ("LastTaskResult: {0}" -f $taskInfo.LastTaskResult)
    }
    else {
        Write-Host "Unable to read scheduled task run info." -ForegroundColor Yellow
    }
}
else {
    Write-Check -Name "Scheduled Task exists" -Ok $false -Detail $taskName
}

Write-Section "JSONL Record Counts"

$dataDir = Join-Path $RepoRoot "data"
$jsonlFiles = @(Get-ChildItem -LiteralPath $dataDir -Filter "*.jsonl" -File -ErrorAction SilentlyContinue | Sort-Object Name)

if ($jsonlFiles.Count -eq 0) {
    Write-Host "No data/*.jsonl files found." -ForegroundColor Yellow
}
else {
    foreach ($file in $jsonlFiles) {
        $count = Get-JsonlLineCount -Path $file.FullName
        if ($null -eq $count) {
            Write-Host ("{0}: unavailable" -f $file.Name) -ForegroundColor Yellow
        }
        else {
            Write-Host ("{0}: {1}" -f $file.Name, $count)
        }
    }
}

Write-Section "Recent Logs"

$logsDir = Join-Path $RepoRoot "logs"
$logs = @(Get-ChildItem -LiteralPath $logsDir -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5)

if ($logs.Count -eq 0) {
    Write-Host "No logs found."
}
else {
    foreach ($log in $logs) {
        Write-Host ("{0} | {1} bytes | {2}" -f $log.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"), $log.Length, $log.Name)
    }
}

Write-Section "Recent Reports"

$reportsDir = Join-Path $RepoRoot "reports"
$reports = @(Get-ChildItem -LiteralPath $reportsDir -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5)

if ($reports.Count -eq 0) {
    Write-Host "No reports found."
}
else {
    foreach ($report in $reports) {
        Write-Host ("{0} | {1} bytes | {2}" -f $report.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"), $report.Length, $report.Name)
    }
}

Write-Section "Git Status"

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if ($gitCommand) {
    & git status --short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "git status --short failed with exit code $LASTEXITCODE." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Git command was not found in PATH." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Health check completed."
