[CmdletBinding()]
param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [switch]$AutoCommit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExitCode = 0
$TranscriptStarted = $false
$AutoCommitPhaseStarted = $false
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

function Write-ManualCommitMessage {
    $messageBytes = [byte[]](
        232, 179, 135, 230, 150, 153, 229, 183, 178, 230, 155, 180,
        230, 150, 176, 232, 136, 135, 229, 144, 140, 230, 173, 165,
        239, 188, 140, 232, 171, 139, 228, 186, 186, 229, 183, 165,
        230, 170, 162, 230, 159, 165, 229, 190, 140, 32, 99, 111,
        109, 109, 105, 116
    )
    Write-Host ([System.Text.Encoding]::UTF8.GetString($messageBytes)) -ForegroundColor Yellow
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "STEP: $Name" -ForegroundColor Cyan
    $global:LASTEXITCODE = 0
    & $Command

    if ($global:LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $global:LASTEXITCODE."
    }
}

try {
    Set-Location -LiteralPath $RepoRoot

    $ParsedDate = [datetime]::MinValue
    $ValidDate = [datetime]::TryParseExact(
        $Date,
        "yyyy-MM-dd",
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None,
        [ref]$ParsedDate
    )

    if (-not $ValidDate) {
        throw "Date must use yyyy-MM-dd format, for example: 2026-06-29."
    }

    $LogsDir = Join-Path $RepoRoot "logs"
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    $LogPath = Join-Path $LogsDir "daily_update_$Date.log"

    Start-Transcript -Path $LogPath -Append | Out-Null
    $TranscriptStarted = $true

    Write-Host "Daily update started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"
    Write-Host "Repository: $RepoRoot"
    Write-Host "Date: $Date"
    Write-Host "AutoCommit: $($AutoCommit.IsPresent)"
    Write-Host "Log: $LogPath"

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git command was not found. Install Git or add it to PATH before running this task."
    }

    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python launcher command py was not found. Install Python Launcher or add it to PATH before running this task."
    }

    if (-not (Get-Command powershell.exe -ErrorAction SilentlyContinue)) {
        throw "powershell.exe was not found. This script needs it to run scripts/import_and_update.ps1."
    }

    $InsideGitRepo = (& git rev-parse --is-inside-work-tree 2>&1)
    if (($global:LASTEXITCODE -ne 0) -or (($InsideGitRepo | Out-String).Trim() -ne "true")) {
        throw "Current directory is not inside a Git repository."
    }

    $IncomingDir = Join-Path $RepoRoot "incoming"
    if (-not (Test-Path -LiteralPath $IncomingDir -PathType Container)) {
        throw "incoming/ directory was not found."
    }

    $IncomingTextFiles = @(Get-ChildItem -LiteralPath $IncomingDir -Filter "*.txt" -File -ErrorAction SilentlyContinue)
    if ($IncomingTextFiles.Count -eq 0) {
        throw "No .txt files found in incoming/. Daily update stopped."
    }

    Write-Host "Found $($IncomingTextFiles.Count) .txt file(s) in incoming/."

    Invoke-Step -Name "Run scripts/import_and_update.ps1" -Command {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\import_and_update.ps1")
    }

    Invoke-Step -Name "Run scripts/sync_to_supabase.py" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\sync_to_supabase.py")
    }

    Invoke-Step -Name "Run scripts/test_supabase_search.py" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\test_supabase_search.py")
    }

    Invoke-Step -Name "Show git status --short" -Command {
        & git status --short
    }

    if ($AutoCommit.IsPresent) {
        $AutoCommitPhaseStarted = $true

        Invoke-Step -Name "Stage daily update files" -Command {
            & git add data daily docs ai_exports
        }

        Invoke-Step -Name "Commit daily reading records" -Command {
            & git commit -m "Add $Date reading records"
        }

        Invoke-Step -Name "Push daily reading records" -Command {
            & git push
        }
    }
    else {
        Write-Host ""
        Write-ManualCommitMessage
    }

    Invoke-Step -Name "Show final git status" -Command {
        & git status
    }

    Write-Host ""
    Write-Host "Daily update completed." -ForegroundColor Green
}
catch {
    $ExitCode = 1
    Write-Host ""
    Write-Host "Daily update failed: $($_.Exception.Message)" -ForegroundColor Red

    if ($AutoCommitPhaseStarted) {
        Write-Host "The AutoCommit block stopped at the failing step. Check git status before retrying." -ForegroundColor Red
    }
    else {
        Write-Host "No commit or push was attempted." -ForegroundColor Red
    }
}
finally {
    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }
}

exit $ExitCode

