[CmdletBinding()]
param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [switch]$AutoCommit,
    [switch]$SkipSupabase
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExitCode = 0
$TranscriptStarted = $false
$AutoCommitPhaseStarted = $false
$ReportWritten = $false
$FailureMessage = ""

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$LogsDir = $null
$ReportsDir = $null
$LogPath = $null
$ReportPath = $null

$IncomingFileInfos = @()
$MovedIncomingFiles = @()
$BeforeCounts = [ordered]@{}
$DatabaseStats = [ordered]@{}
$NewRecordsAdded = 0
$SupabaseSyncStatus = "Not run"
$SupabaseSearchStatus = "Not run"
$GitStatusShort = ""
$NextSteps = @()

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
    $output = @(& $Command 2>&1)
    $exitCode = $global:LASTEXITCODE

    foreach ($line in $output) {
        Write-Host $line
    }

    if ($exitCode -ne 0) {
        throw "$Name failed with exit code $exitCode."
    }

    return $output
}

function Get-JsonlRecordCounts {
    $counts = [ordered]@{}
    $files = @(
        "papers.jsonl",
        "academic_usage.jsonl",
        "research_horizon.jsonl",
        "concept_index.jsonl"
    )

    foreach ($file in $files) {
        $path = Join-Path $RepoRoot (Join-Path "data" $file)
        $count = 0

        if (Test-Path -LiteralPath $path -PathType Leaf) {
            foreach ($line in [System.IO.File]::ReadLines($path, [System.Text.Encoding]::UTF8)) {
                if (-not [string]::IsNullOrWhiteSpace($line)) {
                    $count += 1
                }
            }
        }

        $counts[$file] = $count
    }

    return $counts
}

function Get-NewRecordCount {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Before,

        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$After
    )

    $total = 0

    foreach ($key in $After.Keys) {
        $beforeValue = 0
        if ($Before.Contains($key)) {
            $beforeValue = [int]$Before[$key]
        }

        $delta = [int]$After[$key] - $beforeValue
        if ($delta -gt 0) {
            $total += $delta
        }
    }

    return $total
}

function Get-UniqueDestinationPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Directory,

        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $destination = Join-Path $Directory $FileName
    if (-not (Test-Path -LiteralPath $destination)) {
        return $destination
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    $extension = [System.IO.Path]::GetExtension($FileName)
    $counter = 1

    do {
        $candidate = Join-Path $Directory ("{0}_{1}{2}" -f $baseName, $counter, $extension)
        $counter += 1
    } while (Test-Path -LiteralPath $candidate)

    return $candidate
}

function Move-IncomingTextFiles {
    param(
        [Parameter(Mandatory = $true)]
        [array]$Files
    )

    if ($Files.Count -eq 0) {
        return @()
    }

    $processedDir = Join-Path $RepoRoot (Join-Path "incoming\processed" $Date)
    New-Item -ItemType Directory -Path $processedDir -Force | Out-Null

    $moved = @()

    foreach ($file in $Files) {
        if (-not (Test-Path -LiteralPath $file.FullName -PathType Leaf)) {
            continue
        }

        $destination = Get-UniqueDestinationPath -Directory $processedDir -FileName $file.Name
        Move-Item -LiteralPath $file.FullName -Destination $destination

        $moved += [pscustomobject]@{
            Source = $file.FullName
            Destination = $destination
        }

        Write-Host "Moved incoming file to processed: $($file.Name)"
    }

    return $moved
}

function Set-DefaultNextSteps {
    $script:NextSteps = @()

    if ($script:FailureMessage) {
        $script:NextSteps += "Fix the failed step shown in the log, then rerun the daily update."
        $script:NextSteps += "Do not commit until validation and synchronization requirements have passed."
        return
    }

    if ($SkipSupabase.IsPresent) {
        $script:NextSteps += "Review local data, docs/data, and ai_exports changes."
        $script:NextSteps += "Run the workflow again without -SkipSupabase before relying on Supabase-backed search."
    }
    else {
        $script:NextSteps += "Review the generated data, exports, Supabase sync result, and search test result."
    }

    if ($AutoCommit.IsPresent) {
        $script:NextSteps += "AutoCommit was requested; verify the final git status and remote push result."
    }
    else {
        $script:NextSteps += "Commit manually after review if the changes are correct."
    }
}

function Write-UpdateReport {
    if (-not $ReportPath) {
        return
    }

    if ($DatabaseStats.Count -eq 0) {
        $script:DatabaseStats = Get-JsonlRecordCounts
    }

    if (-not $GitStatusShort) {
        if (Get-Command git -ErrorAction SilentlyContinue) {
            $gitOutput = @(& git status --short 2>&1)
            if ($global:LASTEXITCODE -eq 0) {
                $script:GitStatusShort = ($gitOutput | Out-String).TrimEnd()
            }
            elseif (-not $script:GitStatusShort) {
                $script:GitStatusShort = "Unable to collect git status --short."
            }
        }
        else {
            $script:GitStatusShort = "Git command was not found."
        }
    }

    Set-DefaultNextSteps

    $incomingLines = @()
    if ($IncomingFileInfos.Count -eq 0) {
        $incomingLines += "- None"
    }
    else {
        foreach ($file in $IncomingFileInfos) {
            $incomingLines += "- $($file.Name) ($($file.Length) bytes)"
        }
    }

    $movedLines = @()
    if ($MovedIncomingFiles.Count -eq 0) {
        $movedLines += "- None"
    }
    else {
        foreach ($file in $MovedIncomingFiles) {
            $movedLines += "- $($file.Source) -> $($file.Destination)"
        }
    }

    $statsLines = @()
    foreach ($key in $DatabaseStats.Keys) {
        $statsLines += "- {0}: {1}" -f $key, $DatabaseStats[$key]
    }

    if ($statsLines.Count -eq 0) {
        $statsLines += "- Not available"
    }

    $gitBlock = $GitStatusShort
    if (-not $gitBlock) {
        $gitBlock = "(clean or no output)"
    }

    $status = "Succeeded"
    if ($FailureMessage) {
        $status = "Failed"
    }

    $lines = @(
        "# Daily Update Report - $Date",
        "",
        "## Run metadata",
        "",
        "- Execution date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")",
        "- Date parameter: $Date",
        "- Status: $status",
        "- AutoCommit: $($AutoCommit.IsPresent)",
        "- SkipSupabase: $($SkipSupabase.IsPresent)",
        "- Log file: $LogPath",
        "",
        "## Incoming files",
        ""
    )

    $lines += $incomingLines
    $lines += @(
        "",
        "## Processed incoming files",
        ""
    )
    $lines += $movedLines
    $lines += @(
        "",
        "## New records",
        "",
        "- New records added: $NewRecordsAdded",
        "",
        "## Database statistics",
        ""
    )
    $lines += $statsLines
    $lines += @(
        "",
        "## Supabase",
        "",
        "- Sync status: $SupabaseSyncStatus",
        "- Search test status: $SupabaseSearchStatus",
        "",
        "## Git status short",
        "",
        "```text",
        $gitBlock,
        "```",
        "",
        "## Next steps",
        ""
    )
    foreach ($step in $NextSteps) {
        $lines += "- $step"
    }

    if ($FailureMessage) {
        $lines += @(
            "",
            "## Failure",
            "",
            "- $FailureMessage"
        )
    }

    New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null
    Set-Content -LiteralPath $ReportPath -Value $lines -Encoding UTF8
    $script:ReportWritten = $true
    Write-Host "Report written: $ReportPath"
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
    $ReportsDir = Join-Path $RepoRoot "reports"
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null

    $LogPath = Join-Path $LogsDir "daily_update_$Date.log"
    $ReportPath = Join-Path $ReportsDir "${Date}_update_report.md"

    Start-Transcript -Path $LogPath -Append | Out-Null
    $TranscriptStarted = $true

    Write-Host "Daily update started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"
    Write-Host "Repository: $RepoRoot"
    Write-Host "Date: $Date"
    Write-Host "AutoCommit: $($AutoCommit.IsPresent)"
    Write-Host "SkipSupabase: $($SkipSupabase.IsPresent)"
    Write-Host "Log: $LogPath"
    Write-Host "Report: $ReportPath"

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git command was not found. Install Git or add it to PATH before running this task."
    }

    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python launcher command py was not found. Install Python Launcher or add it to PATH before running this task."
    }

    if (-not (Get-Command powershell.exe -ErrorAction SilentlyContinue)) {
        throw "powershell.exe was not found. This script needs it to run scripts/import_and_update.ps1."
    }

    $insideGitRepoOutput = @(& git rev-parse --is-inside-work-tree 2>&1)
    if (($global:LASTEXITCODE -ne 0) -or (($insideGitRepoOutput | Out-String).Trim() -ne "true")) {
        throw "Current directory is not inside a Git repository."
    }

    $IncomingDir = Join-Path $RepoRoot "incoming"
    if (-not (Test-Path -LiteralPath $IncomingDir -PathType Container)) {
        throw "incoming/ directory was not found."
    }

    $IncomingFileInfos = @(Get-ChildItem -LiteralPath $IncomingDir -Filter "*.txt" -File -ErrorAction SilentlyContinue)
    if ($IncomingFileInfos.Count -eq 0) {
        throw "No .txt files found in incoming/. Daily update stopped."
    }

    Write-Host "Found $($IncomingFileInfos.Count) .txt file(s) in incoming/."

    $BeforeCounts = Get-JsonlRecordCounts

    Invoke-Step -Name "Run scripts/import_and_update.ps1" -Command {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\import_and_update.ps1")
    } | Out-Null

    Invoke-Step -Name "Validate JSONL schema" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\validate_data.py")
    } | Out-Null

    Invoke-Step -Name "Check data integrity" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\check_integrity.py")
    } | Out-Null

    Invoke-Step -Name "Build docs/data" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\build_site_data.py")
    } | Out-Null

    Invoke-Step -Name "Build ai_exports" -Command {
        & py -3 (Join-Path $RepoRoot "scripts\build_ai_exports.py")
    } | Out-Null

    $DatabaseStats = Get-JsonlRecordCounts
    $NewRecordsAdded = Get-NewRecordCount -Before $BeforeCounts -After $DatabaseStats

    if ($SkipSupabase.IsPresent) {
        $SupabaseSyncStatus = "Skipped"
        $SupabaseSearchStatus = "Skipped"
        Write-Host ""
        Write-Host "Supabase steps skipped." -ForegroundColor Yellow
    }
    else {
        $SupabaseSyncStatus = "Failed"
        Invoke-Step -Name "Run scripts/sync_to_supabase.py" -Command {
            & py -3 (Join-Path $RepoRoot "scripts\sync_to_supabase.py")
        } | Out-Null
        $SupabaseSyncStatus = "Succeeded"

        $SupabaseSearchStatus = "Failed"
        Invoke-Step -Name "Run scripts/test_supabase_search.py" -Command {
            & py -3 (Join-Path $RepoRoot "scripts\test_supabase_search.py")
        } | Out-Null
        $SupabaseSearchStatus = "Succeeded"
    }

    $MovedIncomingFiles = @(Move-IncomingTextFiles -Files $IncomingFileInfos)

    $GitStatusShort = ((Invoke-Step -Name "Show git status --short" -Command {
        & git status --short
    }) | Out-String).TrimEnd()

    Write-UpdateReport

    if ($AutoCommit.IsPresent) {
        $AutoCommitPhaseStarted = $true

        Invoke-Step -Name "Stage daily update files" -Command {
            & git add data daily docs ai_exports incoming/processed reports
        } | Out-Null

        Invoke-Step -Name "Commit daily reading records" -Command {
            & git commit -m "Add $Date reading records"
        } | Out-Null

        Invoke-Step -Name "Push daily reading records" -Command {
            & git push
        } | Out-Null
    }
    else {
        Write-Host ""
        Write-ManualCommitMessage
    }

    Invoke-Step -Name "Show final git status" -Command {
        & git status
    } | Out-Null

    Write-Host ""
    Write-Host "Daily update completed." -ForegroundColor Green
}
catch {
    $ExitCode = 1
    $FailureMessage = $_.Exception.Message
    Write-Host ""
    Write-Host "Daily update failed: $FailureMessage" -ForegroundColor Red

    if ($AutoCommitPhaseStarted) {
        Write-Host "The AutoCommit block stopped at the failing step. Check git status before retrying." -ForegroundColor Red
    }
    else {
        Write-Host "No commit or push was attempted." -ForegroundColor Red
    }
}
finally {
    try {
        if ($ReportPath -and (-not $ReportWritten)) {
            Write-UpdateReport
        }
    }
    catch {
        Write-Host "Failed to write update report: $($_.Exception.Message)" -ForegroundColor Red
    }

    if ($TranscriptStarted) {
        Stop-Transcript | Out-Null
    }
}

exit $ExitCode
