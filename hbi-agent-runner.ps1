#Requires -Version 5.1
<#
.SYNOPSIS
  HBI Agent Runner — polls agent-jobs/pending, runs allowlisted commands only.
.NOTES
  Security: allowlist only, repo-root cwd, timeout, no free-form shell.
  After each job: commits ONLY agent-jobs/results/*.log and pushes (closes the loop).
  Stop: Ctrl+C
#>
$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not $RepoRoot) { $RepoRoot = Get-Location }
Set-Location $RepoRoot

$Pending = Join-Path $RepoRoot "agent-jobs\pending"
$Running = Join-Path $RepoRoot "agent-jobs\running"
$Results = Join-Path $RepoRoot "agent-jobs\results"
$Done = Join-Path $RepoRoot "agent-jobs\done"
$AllowFile = Join-Path $RepoRoot "agent-jobs\allowed.txt"
$PollSeconds = 15
# Easy mode for PO: publish logs to GitHub so team reads results without your copy-paste
$AutoPushResults = $true

foreach ($d in @($Pending, $Running, $Results, $Done)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

function Get-AllowList {
    if (-not (Test-Path $AllowFile)) { return @() }
    Get-Content $AllowFile | Where-Object {
        $_ -and ($_ -notmatch '^\s*#') -and ($_ -notmatch '^\s*$')
    } | ForEach-Object { $_.Trim() }
}

function Test-CommandAllowed([string]$Command, [string[]]$Allow) {
    $c = $Command.Trim()
    foreach ($a in $Allow) {
        if ($c -eq $a -or $c.StartsWith($a + " ") -or $c.StartsWith($a + "`t")) {
            return $true
        }
    }
    return $false
}

function Publish-ResultsOnly([string]$JobId) {
    if (-not $AutoPushResults) { return }
    try {
        git add -- "agent-jobs/results/*.log" 2>$null
        # Remove completed job from pending tracking on remote if still listed — only results staged
        $status = git status --porcelain -- "agent-jobs/results"
        if (-not $status) {
            Write-Host "[PUBLISH] nothing new to push" -ForegroundColor Gray
            return
        }
        git commit -m "agent-result: $JobId" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[PUBLISH] commit skipped (no change or error)" -ForegroundColor Gray
            return
        }
        git push origin master 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PUBLISH] results pushed → team can read on GitHub" -ForegroundColor Green
        }
        else {
            Write-Host "[PUBLISH] push failed — log is local only" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "[PUBLISH] $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

function Write-Banner {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " HBI Agent Runner (SECURE + AUTO RESULT)" -ForegroundColor Cyan
    Write-Host " Repo : $RepoRoot" -ForegroundColor Cyan
    Write-Host " Poll : ${PollSeconds}s | AutoPushResults=$AutoPushResults" -ForegroundColor Cyan
    Write-Host " Ctrl+C to stop" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Invoke-AgentJob([string]$JobPath) {
    $name = [IO.Path]::GetFileNameWithoutExtension($JobPath)
    $raw = Get-Content -Raw -Path $JobPath -Encoding UTF8
    $job = $raw | ConvertFrom-Json
    $id = if ($job.id) { $job.id } else { $name }
    $timeout = 120
    if ($job.timeout_sec) { $timeout = [int]$job.timeout_sec }
    if ($timeout -lt 10) { $timeout = 10 }
    if ($timeout -gt 300) { $timeout = 300 }

    $cmd = [string]$job.command
    $argList = @()
    if ($job.args) { $argList = @($job.args | ForEach-Object { [string]$_ }) }

    $fullForAllow = ($cmd + " " + ($argList -join " ")).Trim()
    $allow = Get-AllowList
    $log = Join-Path $Results "$id.log"
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $headSha = ""
    try { $headSha = (git rev-parse --short HEAD 2>$null) } catch {}

    $header = @(
        "HBI AGENT RESULT"
        "id=$id"
        "from=$($job.from)"
        "started=$stamp"
        "commit=$headSha"
        "command=$cmd"
        "args=$($argList -join ' ')"
        "repo=$RepoRoot"
        "----------------------------------------"
    )
    $header | Set-Content -Path $log -Encoding UTF8

    if (-not (Test-CommandAllowed -Command $cmd -Allow $allow)) {
        Add-Content $log "STATUS=REJECTED_NOT_ALLOWLISTED"
        Add-Content $log "Full=$fullForAllow"
        Write-Host "[REJECT] $id — not allowlisted" -ForegroundColor Red
        Publish-ResultsOnly -JobId $id
        return
    }

    $exe = $null
    $passArgs = @()
    if ($cmd -match '^python(\s|$)') {
        $exe = "python"
        $rest = $cmd.Substring(6).Trim()
        if ($rest) { $passArgs += ($rest -split '\s+') }
        $passArgs += $argList
    }
    elseif ($cmd -match '^git(\s|$)') {
        $exe = "git"
        $rest = $cmd.Substring(3).Trim()
        if ($rest) { $passArgs += ($rest -split '\s+') }
        $passArgs += $argList
    }
    else {
        Add-Content $log "STATUS=REJECTED_UNSUPPORTED_EXECUTABLE"
        Write-Host "[REJECT] $id — executable not python/git" -ForegroundColor Red
        Publish-ResultsOnly -JobId $id
        return
    }

    Write-Host "[RUN] $id → $exe $($passArgs -join ' ')" -ForegroundColor Yellow
    $outFile = Join-Path $env:TEMP "hbi-agent-$id-out.txt"
    $errFile = Join-Path $env:TEMP "hbi-agent-$id-err.txt"

    try {
        $p = Start-Process -FilePath $exe -ArgumentList $passArgs `
            -WorkingDirectory $RepoRoot `
            -RedirectStandardOutput $outFile `
            -RedirectStandardError $errFile `
            -NoNewWindow -PassThru
        $finished = $p.WaitForExit($timeout * 1000)
        if (-not $finished) {
            try { $p.Kill() } catch {}
            Add-Content $log "STATUS=TIMEOUT after ${timeout}s"
            Write-Host "[TIMEOUT] $id" -ForegroundColor Red
        }
        else {
            $code = $p.ExitCode
            if ($null -eq $code) { $code = -1 }
            Add-Content $log "STATUS=EXIT_CODE=$code"
            if ($code -eq 0) {
                Write-Host "[OK] $id exit=0" -ForegroundColor Green
            }
            else {
                Write-Host "[FAIL] $id exit=$code" -ForegroundColor Red
            }
        }
        if (Test-Path $outFile) {
            Add-Content $log "--- STDOUT ---"
            Get-Content $outFile -ErrorAction SilentlyContinue | Add-Content $log
        }
        if (Test-Path $errFile) {
            Add-Content $log "--- STDERR ---"
            Get-Content $errFile -ErrorAction SilentlyContinue | Add-Content $log
        }
    }
    catch {
        Add-Content $log "STATUS=ERROR"
        Add-Content $log $_.Exception.Message
        Write-Host "[ERROR] $id $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Remove-Item $outFile, $errFile -ErrorAction SilentlyContinue
        Add-Content $log "----------------------------------------"
        Add-Content $log "finished=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        Publish-ResultsOnly -JobId $id
    }
}

Write-Banner
Write-Host "Allowlist loaded: $((Get-AllowList).Count) entries" -ForegroundColor Gray

while ($true) {
    try {
        git pull --ff-only origin master 2>$null | Out-Null
    } catch {}

    $jobs = @(Get-ChildItem -Path $Pending -Filter "*.json" -File -ErrorAction SilentlyContinue)
    foreach ($j in $jobs) {
        $dest = Join-Path $Running $j.Name
        $donePath = Join-Path $Done $j.Name
        try {
            Move-Item -Path $j.FullName -Destination $dest -Force
            Invoke-AgentJob -JobPath $dest
            Move-Item -Path $dest -Destination $donePath -Force -ErrorAction SilentlyContinue
            if (Test-Path $dest) { Remove-Item -Path $dest -Force -ErrorAction SilentlyContinue }
        }
        catch {
            Write-Host "[ERROR] processing $($j.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds $PollSeconds
}
