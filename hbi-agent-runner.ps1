#Requires -Version 5.1
<#
.SYNOPSIS
  HBI Agent Runner — polls agent-jobs/pending, runs allowlisted commands only.
.NOTES
  Security: allowlist only, repo-root cwd, timeout, no free-form shell.
  Stop: Ctrl+C
#>
$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
if (-not $RepoRoot) { $RepoRoot = Get-Location }
Set-Location $RepoRoot

$Pending = Join-Path $RepoRoot "agent-jobs\pending"
$Running = Join-Path $RepoRoot "agent-jobs\running"
$Results = Join-Path $RepoRoot "agent-jobs\results"
$AllowFile = Join-Path $RepoRoot "agent-jobs\allowed.txt"
$PollSeconds = 15

foreach ($d in @($Pending, $Running, $Results)) {
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

function Write-Banner {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " HBI Agent Runner (SECURE)" -ForegroundColor Cyan
    Write-Host " Repo : $RepoRoot" -ForegroundColor Cyan
    Write-Host " Poll : ${PollSeconds}s | Ctrl+C to stop" -ForegroundColor Cyan
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

    $header = @(
        "HBI AGENT RESULT"
        "id=$id"
        "from=$($job.from)"
        "started=$stamp"
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
        return
    }

    # Only python or git as executable; args separate (no Invoke-Expression of whole string)
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
            Add-Content $log "STATUS=EXIT_CODE=$($p.ExitCode)"
            if ($p.ExitCode -eq 0) {
                Write-Host "[OK] $id exit=0" -ForegroundColor Green
            }
            else {
                Write-Host "[FAIL] $id exit=$($p.ExitCode)" -ForegroundColor Red
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
    }
}

Write-Banner
Write-Host "Allowlist loaded: $((Get-AllowList).Count) entries" -ForegroundColor Gray

while ($true) {
    try {
        # Optional quiet pull so jobs from GitHub appear (minimal network)
        git pull --ff-only origin master 2>$null | Out-Null
    } catch {}

    $jobs = @(Get-ChildItem -Path $Pending -Filter "*.json" -File -ErrorAction SilentlyContinue)
    foreach ($j in $jobs) {
        $dest = Join-Path $Running $j.Name
        try {
            Move-Item -Path $j.FullName -Destination $dest -Force
            Invoke-AgentJob -JobPath $dest
            Remove-Item -Path $dest -Force -ErrorAction SilentlyContinue
        }
        catch {
            Write-Host "[ERROR] processing $($j.Name): $($_.Exception.Message)" -ForegroundColor Red
            # leave file in running for inspection
        }
    }
    Start-Sleep -Seconds $PollSeconds
}
