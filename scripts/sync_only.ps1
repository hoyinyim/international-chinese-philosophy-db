[CmdletBinding()]
param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$TranscriptStarted = $false
$ExitCode = 0

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

    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python launcher command py was not found. Install Python Launcher or add it to PATH before running this task."
    }

    $LogsDir = Join-Path $RepoRoot "logs"
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    $LogPath = Join-Path $LogsDir "sync_only_$Date.log"

    Start-Transcript -Path $LogPath -Append | Out-Null
    $TranscriptStarted = $true

    Write-Host "Supabase sync-only run started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"
    Write-Host "Repository: $RepoRoot"
    Write-Host "Date: $Date"
    Write-Host "Log: $LogPath"
    Write-Host "This script does not import records, modify incoming/, commit, or push."

    Invoke-Step -Name "Run scripts/sync_to_supabase.py" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\sync_to_supabase.py")
    }

    Invoke-Step -Name "Run scripts/test_supabase_search.py" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\test_supabase_search.py")
    }

    Write-Host ""
    Write-Host "Supabase sync-only run completed." -ForegroundColor Green
}
catch {
    $ExitCode = 1
    Write-Host ""
    Write-Host "Supabase sync-only run failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "No import, incoming/ changes, commit, or push was attempted." -ForegroundColor Red
}
finally {
    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }
}

exit $ExitCode
