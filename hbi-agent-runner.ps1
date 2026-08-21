#Requires -Version 5.1
<#
.SYNOPSIS
  HBI Agent Runner — polls agent-jobs/pending, runs allowlisted commands only.
.NOTES
  Security: allowlist only, repo-root cwd, timeout, no free-form shell.
  After each job: commits ONLY the specific results/<id>.log and pushes.
  Stop: Ctrl+C
#>
$ErrorActionPreference = "Continue"
$RepoRoot = $PSScriptRoot
if (-not $RepoRoot) { $RepoRoot = (Get-Location).Path }
Set-Location $RepoRoot

$Pending = Join-Path $RepoRoot "agent-jobs\pending"
$Running = Join-Path $RepoRoot "agent-jobs\running"
$Results = Join-Path $RepoRoot "agent-jobs\results"
$Done = Join-Path $RepoRoot "agent-jobs\done"
$AllowFile = Join-Path $RepoRoot "agent-jobs\allowed.txt"
$PollSeconds = 15
$AutoPushResults = $true

foreach ($d in @($Pending, $Running, $Results, $Done)) {
    if (-not (Test-Path -LiteralPath $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
}

function Get-AllowList {
    if (-not (Test-Path -LiteralPath $AllowFile)) { return @() }
    Get-Content -LiteralPath $AllowFile | Where-Object {
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

function Publish-ResultLog([string]$LogPath, [string]$JobId) {
    if (-not $AutoPushResults) { return }
    if (-not (Test-Path -LiteralPath $LogPath)) {
        Write-Host "[PUBLISH] log missing: $LogPath" -ForegroundColor Yellow
        return
    }
    try {
        # Explicit file path — Windows git does not expand *.log globs reliably
        git add --literal-pathspec -- "$LogPath" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            git add -- "$LogPath" 2>&1 | Out-Null
        }
        $porcelain = git status --porcelain -- "agent-jobs/results"
        if (-not $porcelain) {
            Write-Host "[PUBLISH] nothing new to push" -ForegroundColor Gray
            return
        }
        git commit -m "agent-result: $JobId" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[PUBLISH] commit skipped" -ForegroundColor Gray
            return
        }
        git push origin master 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PUBLISH] OK → $LogPath on GitHub" -ForegroundColor Green
        }
        else {
            Write-Host "[PUBLISH] push failed — log is local: $LogPath" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "[PUBLISH] $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

function Write-Banner {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " HBI Agent Runner v1.1 (Windows-safe)" -ForegroundColor Cyan
    Write-Host " Repo : $RepoRoot" -ForegroundColor Cyan
    Write-Host " Poll : ${PollSeconds}s | AutoPush=$AutoPushResults" -ForegroundColor Cyan
    Write-Host " Ctrl+C to stop" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Invoke-AgentJob([string]$JobPath) {
    $name = [IO.Path]::GetFileNameWithoutExtension($JobPath)
    $raw = Get-Content -Raw -LiteralPath $JobPath -Encoding UTF8
    $job = $raw | ConvertFrom-Json
    $id = if ($job.id) { [string]$job.id } else { $name }
    $timeout = 120
    if ($job.timeout_sec) { $timeout = [int]$job.timeout_sec }
    if ($timeout -lt 10) { $timeout = 10 }
    if ($timeout -gt 300) { $timeout = 300 }

    $cmd = [string]$job.command
    $argList = @()
    if ($job.args) { $argList = @($job.args | ForEach-Object { [string]$_ }) }

    $allow = Get-AllowList
    $log = Join-Path $Results ($id + ".log")
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $headSha = ""
    try { $headSha = (git rev-parse --short HEAD 2>$null) } catch {}

    @("HBI AGENT RESULT",
      "id=$id",
      "from=$($job.from)",
      "started=$stamp",
      "commit=$headSha",
      "command=$cmd",
      "args=$($argList -join ' ')",
      "repo=$RepoRoot",
      "----------------------------------------") |
        Set-Content -LiteralPath $log -Encoding UTF8

    Write-Host "[LOG] $log" -ForegroundColor Gray

    if (-not (Test-CommandAllowed -Command $cmd -Allow $allow)) {
        Add-Content -LiteralPath $log "STATUS=REJECTED_NOT_ALLOWLISTED"
        Write-Host "[REJECT] $id" -ForegroundColor Red
        Publish-ResultLog -LogPath $log -JobId $id
        return
    }

    $exe = $null
    $passArgs = New-Object System.Collections.Generic.List[string]
    if ($cmd -match '^python(\s|$)') {
        $exe = "python"
        $rest = $cmd.Substring(6).Trim()
        if ($rest) {
            foreach ($p in ($rest -split '\s+')) { if ($p) { [void]$passArgs.Add($p) } }
        }
        foreach ($a in $argList) { [void]$passArgs.Add($a) }
    }
    elseif ($cmd -match '^git(\s|$)') {
        $exe = "git"
        $rest = $cmd.Substring(3).Trim()
        if ($rest) {
            foreach ($p in ($rest -split '\s+')) { if ($p) { [void]$passArgs.Add($p) } }
        }
        foreach ($a in $argList) { [void]$passArgs.Add($a) }
    }
    else {
        Add-Content -LiteralPath $log "STATUS=REJECTED_UNSUPPORTED_EXECUTABLE"
        Write-Host "[REJECT] $id" -ForegroundColor Red
        Publish-ResultLog -LogPath $log -JobId $id
        return
    }

    $argArray = $passArgs.ToArray()
    Write-Host "[RUN] $id → $exe $($argArray -join ' ')" -ForegroundColor Yellow

    $outFile = Join-Path $env:TEMP ("hbi-agent-" + $id + "-out.txt")
    $errFile = Join-Path $env:TEMP ("hbi-agent-" + $id + "-err.txt")
    Remove-Item -LiteralPath $outFile, $errFile -ErrorAction SilentlyContinue

    $code = -999
    try {
        $p = Start-Process -FilePath $exe `
            -ArgumentList $argArray `
            -WorkingDirectory $RepoRoot `
            -RedirectStandardOutput $outFile `
            -RedirectStandardError $errFile `
            -NoNewWindow -PassThru

        $finished = $p.WaitForExit($timeout * 1000)
        if (-not $finished) {
            try { $p.Kill() } catch {}
            Add-Content -LiteralPath $log "STATUS=TIMEOUT after ${timeout}s"
            Write-Host "[TIMEOUT] $id" -ForegroundColor Red
            $code = -2
        }
        else {
            # Windows: refresh process object before reading ExitCode
            try { $p.Refresh() } catch {}
            Start-Sleep -Milliseconds 200
            if ($null -ne $p.ExitCode) { $code = [int]$p.ExitCode } else { $code = -1 }
            Add-Content -LiteralPath $log "STATUS=EXIT_CODE=$code"
            if ($code -eq 0) {
                Write-Host "[OK] $id exit=0" -ForegroundColor Green
            }
            else {
                Write-Host "[FAIL] $id exit=$code (see log; pytest text may still show passed)" -ForegroundColor Yellow
            }
        }

        if (Test-Path -LiteralPath $outFile) {
            Add-Content -LiteralPath $log "--- STDOUT ---"
            Get-Content -LiteralPath $outFile -ErrorAction SilentlyContinue | Add-Content -LiteralPath $log
        }
        if (Test-Path -LiteralPath $errFile) {
            Add-Content -LiteralPath $log "--- STDERR ---"
            Get-Content -LiteralPath $errFile -ErrorAction SilentlyContinue | Add-Content -LiteralPath $log
        }
    }
    catch {
        Add-Content -LiteralPath $log "STATUS=ERROR"
        Add-Content -LiteralPath $log $_.Exception.Message
        Write-Host "[ERROR] $id $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Remove-Item -LiteralPath $outFile, $errFile -ErrorAction SilentlyContinue
        Add-Content -LiteralPath $log "----------------------------------------"
        Add-Content -LiteralPath $log "finished=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        if (Test-Path -LiteralPath $log) {
            Write-Host "[LOG written] $log" -ForegroundColor Gray
        }
        Publish-ResultLog -LogPath $log -JobId $id
    }
}

Write-Banner
Write-Host "Allowlist: $((Get-AllowList).Count) entries" -ForegroundColor Gray

while ($true) {
    try { git pull --ff-only origin master 2>$null | Out-Null } catch {}

    $jobs = @(Get-ChildItem -LiteralPath $Pending -Filter "*.json" -File -ErrorAction SilentlyContinue)
    foreach ($j in $jobs) {
        $dest = Join-Path $Running $j.Name
        $donePath = Join-Path $Done $j.Name
        try {
            Move-Item -LiteralPath $j.FullName -Destination $dest -Force
            Invoke-AgentJob -JobPath $dest
            Move-Item -LiteralPath $dest -Destination $donePath -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue }
        }
        catch {
            Write-Host "[ERROR] $($j.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds $PollSeconds
}
