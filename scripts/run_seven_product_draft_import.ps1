param(
  [string]$RepoRoot = "E:\HBI_GitHub_Current",
  [string]$ApiBase = "http://127.0.0.1:8000/api/v1"
)
$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$db = Join-Path $RepoRoot "data\hbi.db"
if (-not (Test-Path (Join-Path $RepoRoot "app\main.py"))) { throw "HBI repository not found at $RepoRoot" }
if (-not (Test-Path $db)) { throw "Expected live database not found: $db" }
$listener = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$backend = $null
$reuseExistingBackend = [bool]$listener

if ($reuseExistingBackend) {
  Write-Host "Port 8000 is already serving a process. Checking the existing HBI API; it will not be stopped or replaced."
  try {
    $apiRoot = ([uri]$ApiBase).GetLeftPart([System.UriPartial]::Authority)
    $probe = Invoke-WebRequest "$apiRoot/openapi.json" -UseBasicParsing -TimeoutSec 5
    if ($probe.StatusCode -ne 200) { throw "Unexpected HTTP status $($probe.StatusCode)" }
  } catch {
    throw "Port 8000 is occupied but the existing HBI API could not be verified at $ApiBase. No import attempted. $($_.Exception.Message)"
  }
  Write-Host "Existing API responds successfully. The authenticated importer will validate all seven canonical Product IDs before any write."
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path (Split-Path $db) "hbi.pre-seven-product-drafts-$stamp.db"
$pyBackup = 'import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()'
& python -c $pyBackup $db $backup
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $backup)) { throw "SQLite online backup failed; no import attempted." }
$pyCheck = 'import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); q=bytes([80,82,65,71,77,65,32,105,110,116,101,103,114,105,116,121,95,99,104,101,99,107]).decode(); print(c.execute(q).fetchone()[0]); c.close()'
$integrity = & python -c $pyCheck $backup
if ($LASTEXITCODE -ne 0 -or ($integrity -join "").Trim() -ne "ok") { throw "Backup integrity check failed: $integrity" }
Write-Host "Verified backup: $backup"

$work = Join-Path $env:TEMP "hbi-seven-product-drafts"
New-Item -ItemType Directory -Force -Path $work | Out-Null
$raw = "https://raw.githubusercontent.com/vahidmaghsoudi2/hbi/research/seven-product-evidence-draft-manifest-20261109-master/"
Invoke-WebRequest ($raw + "scripts/apply_seven_product_research_drafts.py") -OutFile (Join-Path $work "apply_seven_product_research_drafts.py")
Invoke-WebRequest ($raw + "docs/product-intake-knowledge-registry/SEVEN_PRODUCT_EVIDENCE_DRAFT_MANIFEST_V1.json") -OutFile (Join-Path $work "manifest.json")

$logOut = Join-Path $work "backend.stdout.log"
$logErr = Join-Path $work "backend.stderr.log"
$ready = $reuseExistingBackend
if (-not $reuseExistingBackend) {
  $backend = Start-Process -FilePath "python" -ArgumentList @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8000") -WorkingDirectory $RepoRoot -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
  for ($i=0; $i -lt 40; $i++) {
    Start-Sleep -Seconds 1
    try {
      $probe = Invoke-WebRequest "http://127.0.0.1:8000/openapi.json" -UseBasicParsing -TimeoutSec 2
      if ($probe.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
    if ($backend.HasExited) { break }
  }
  if (-not $ready) {
    $details = if (Test-Path $logErr) { Get-Content $logErr -Raw } else { "No backend log." }
    throw "Backend failed to start. No import was attempted. $details"
  }
}

$importer = Join-Path $work "apply_seven_product_research_drafts.py"
$manifest = Join-Path $work "manifest.json"
Write-Host ""
Write-Host "=== DRY RUN ==="
& python $importer --api-base $ApiBase --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw "Dry-run failed. No Evidence writes were attempted. Backend PID: $($backend.Id)" }

Write-Host ""
Write-Host "=== APPLY SOURCE-BOUND PENDING DRAFTS ==="
& python $importer --api-base $ApiBase --manifest $manifest --apply
if ($LASTEXITCODE -ne 0) { throw "Import or read-back verification failed. Backend PID: $($backend.Id). Inspect logs in $work" }

Write-Host ""
Write-Host "SUCCESS: PENDING Evidence drafts were written and read back."
Write-Host "Backup: $backup"
if ($backend) { Write-Host "Backend PID: $($backend.Id) (left running)" } else { Write-Host "Backend: existing API reused; no process was stopped or replaced." }
Write-Host "Logs: $work"
