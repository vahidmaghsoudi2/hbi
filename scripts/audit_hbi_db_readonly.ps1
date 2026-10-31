#Requires -Version 5.1
<#
.SYNOPSIS
  HBI — read-only audit of the effective database connection (Windows).

.DESCRIPTION
  Run on the same machine and from the same repo root that actually launches HBI
  (the folder that contains app\main.py and, typically, scripts\start-hbi.bat).

  READ-ONLY guarantees:
  - Does not create/alter/drop tables or columns
  - Does not run migrations
  - Does not backup or restore
  - Does not create temporary files or modify any file
  - Does not stop any process
  - SQLite is opened with mode=ro&immutable=1 (no writes or sidecars)
  - WAL / rollback-journal sidecars cause a safe refusal
  - Backend runtime DATABASE_URL is never inferred from the audit shell
  - Secrets are never printed

.OUTPUT
  Text report to the console. Exit codes:
    0 = report completed (result may still be UNKNOWN / BLOCKED / READY_FOR_REVIEW)
    1 = fatal error (e.g. not run from a repo root)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Section([string]$Title) {
    Write-Host ""
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

function Redact-DatabaseUrl([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) { return "(empty)" }
    $u = $Url.Trim()
    # Strip userinfo (user:pass@) from any URI-like string without printing it.
    if ($u -match '^(?<scheme>[a-zA-Z0-9+.-]+)://(?<userinfo>[^@/?#]+)@(?<rest>.+)$') {
        return "$($Matches['scheme'])://***@$($Matches['rest'])"
    }
    return $u
}

function Get-DatabaseKind([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) { return "EMPTY" }
    $u = $Url.Trim().ToLowerInvariant()
    if ($u -match '^sqlite:') { return "SQLITE" }
    if ($u -match '^postgres(ql)?:') { return "POSTGRESQL" }
    if ($u -match '^mysql:') { return "MYSQL" }
    if ($u -match '^mssql:|^sqlserver:') { return "SQLSERVER" }
    return "OTHER"
}

function Resolve-SqlitePathFromUrl([string]$Url, [string]$RepoRoot) {
    # Returns absolute path or $null if not determinable.
    if ([string]::IsNullOrWhiteSpace($Url)) { return $null }
    $raw = $Url.Trim()
    if ($raw -notmatch '^sqlite:') { return $null }

    $pathPart = $null
    if ($raw -match '^sqlite:////(?<p>.+)$') {
        $pathPart = $Matches['p']
    }
    elseif ($raw -match '^sqlite:///(?<p>.+)$') {
        $pathPart = $Matches['p']
    }
    elseif ($raw -match '^sqlite:(?<p>.+)$') {
        $pathPart = $Matches['p']
    }
    if ([string]::IsNullOrWhiteSpace($pathPart)) { return $null }

    if ($pathPart.StartsWith("./") -or $pathPart.StartsWith(".\")) {
        $pathPart = $pathPart.Substring(2)
    }

    if ($pathPart -match '^[A-Za-z]:[\\/]') {
        return [System.IO.Path]::GetFullPath($pathPart)
    }
    if ($pathPart.StartsWith("\\") -or $pathPart.StartsWith("//")) {
        return [System.IO.Path]::GetFullPath($pathPart)
    }
    if ($pathPart.StartsWith("/")) {
        return $pathPart
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $pathPart))
}

function Test-IsRepoRoot([string]$Path) {
    return (Test-Path -LiteralPath (Join-Path $Path "app\main.py")) -and
           (Test-Path -LiteralPath (Join-Path $Path "app\database.py"))
}

function Get-RunningHbiBackendHints {
    $hints = New-Object System.Collections.Generic.List[string]
    try {
        $procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.CommandLine -and (
                    $_.CommandLine -match 'uvicorn' -and $_.CommandLine -match 'app\.main:app'
                )
            }
        foreach ($p in $procs) {
            # Never emit command lines: they can contain credentials or connection URLs.
            $hints.Add("PID=$($p.ProcessId) PROCESS=$($p.Name) BACKEND_SIGNATURE_MATCHED=yes")
        }
    } catch {
        $hints.Add("(could not query processes: $($_.Exception.Message))")
    }
    return $hints
}

function Invoke-SqliteReadonlyAudit([string]$DbPath) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        return @{ Ok = $false; Error = "python not found in PATH; cannot open SQLite read-only." }
    }

    $code = @'
import json, os, sqlite3, sys, pathlib
path = sys.argv[1]
if not os.path.isfile(path):
    print(json.dumps({"ok": False, "error": "file_not_found"}))
    sys.exit(0)
# Refuse sidecars: read-only audit must not create/change WAL or journal files.
sidecars = [path + "-wal", path + "-shm", path + "-journal"]
present = [p for p in sidecars if os.path.exists(p)]
if present:
    print(json.dumps({"ok": False, "error": "sqlite_sidecar_present",
                      "sidecars": [os.path.basename(p) for p in present]}))
    sys.exit(0)
uri = pathlib.Path(path).resolve().as_uri() + "?mode=ro&immutable=1"
try:
    conn = sqlite3.connect(uri, uri=True, timeout=5.0)
except Exception as e:
    print(json.dumps({"ok": False, "error": "connect_failed", "detail": str(e)}))
    sys.exit(0)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
out = {"ok": True, "path": path, "size_bytes": os.path.getsize(path)}
try:
    out["integrity_check"] = cur.execute("PRAGMA integrity_check").fetchone()[0]
except Exception as e:
    out["integrity_check"] = f"error:{e}"
try:
    fk_rows = cur.execute("PRAGMA foreign_key_check").fetchall()
    out["foreign_key_check_violations"] = len(fk_rows)
except Exception as e:
    out["foreign_key_check_violations"] = f"error:{e}"
tables = {r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
).fetchall()}
out["has_ProductProblemLink"] = "ProductProblemLink" in tables
out["has_ProductProblemLinkAssessmentEvent"] = "ProductProblemLinkAssessmentEvent" in tables
expected_cols = [
    "feature_basis", "outcome", "assertion_key", "revision_no",
    "supersedes_link_id", "idempotency_key", "request_fingerprint",
]
if "ProductProblemLink" in tables:
    cols = [r[1] for r in cur.execute("PRAGMA table_info('ProductProblemLink')").fetchall()]
    out["ProductProblemLink_columns"] = cols
    out["pr496_new_columns_present"] = {c: (c in cols) for c in expected_cols}
    out["ProductProblemLink_row_count"] = cur.execute(
        "SELECT COUNT(*) FROM ProductProblemLink"
    ).fetchone()[0]
else:
    out["ProductProblemLink_columns"] = []
    out["pr496_new_columns_present"] = {c: False for c in expected_cols}
    out["ProductProblemLink_row_count"] = None
if "ProductProblemLinkAssessmentEvent" in tables:
    out["ProductProblemLinkAssessmentEvent_row_count"] = cur.execute(
        "SELECT COUNT(*) FROM ProductProblemLinkAssessmentEvent"
    ).fetchone()[0]
else:
    out["ProductProblemLinkAssessmentEvent_row_count"] = None
idx = cur.execute(
    "SELECT name, type, sql FROM sqlite_master WHERE tbl_name='ProductProblemLink' "
    "AND type IN ('index','trigger') ORDER BY type, name"
).fetchall()
out["ProductProblemLink_indexes_and_triggers"] = [
    {"name": r[0], "type": r[1], "sql": r[2]} for r in idx
]
conn.close()
print(json.dumps(out, ensure_ascii=False))
'@

    # Pass Python source inline; no temporary file is created.
    $jsonText = & $py.Path -c $code $DbPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        return @{ Ok = $false; Error = "python exited $LASTEXITCODE : $jsonText" }
    }
    $obj = $jsonText | ConvertFrom-Json
    return @{ Ok = $true; Data = $obj }
}

Write-Host "HBI read-only database audit" -ForegroundColor Green
Write-Host "Timestamp (local): $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')"

$startDir = (Get-Location).Path
Write-Section "1) Execution location"
Write-Host "Current directory: $startDir"

$repoRoot = $null
if (Test-IsRepoRoot $startDir) {
    $repoRoot = $startDir
} elseif (Test-IsRepoRoot (Split-Path $startDir -Parent)) {
    $repoRoot = (Split-Path $startDir -Parent)
}

if (-not $repoRoot) {
    Write-Host "FATAL: This does not look like an HBI repo root (app\main.py missing)." -ForegroundColor Red
    Write-Host "cd to the folder that contains app\main.py and re-run." -ForegroundColor Yellow
    exit 1
}
Write-Host "Resolved repo root: $repoRoot"
Write-Host "app\main.py: present"

Write-Section "2) Audit-shell setting (not proof of Backend runtime configuration)"
$envUrl = $env:DATABASE_URL
$envWasUnset = ($null -eq $envUrl -or $envUrl -eq "")
Write-Host ("AUDIT_SHELL_DATABASE_URL: " + $(if ($envWasUnset) { "NOT_SET" } else { "SET (value withheld)" }))
Write-Host "BACKEND_RUNTIME_DATABASE_URL: NOT_PROVEN"
if ($envWasUnset) {
    Write-Host "Audit candidate source: code default sqlite:///./data/hbi.db (candidate only)"
    $candidateUrl = "sqlite:///./data/hbi.db"
} else {
    Write-Host "Audit candidate source: DATABASE_URL in this PowerShell process only"
    $candidateUrl = $envUrl
}
$kind = Get-DatabaseKind $candidateUrl
Write-Host "Audit candidate kind: $kind"

$sqlitePath = $null
if ($kind -eq "SQLITE") {
    $sqlitePath = Resolve-SqlitePathFromUrl $candidateUrl $repoRoot
    if ($sqlitePath) {
        Write-Host "Audit candidate path (relative paths resolved against this repo root; NOT runtime proof): $sqlitePath"
    } else {
        Write-Host "Could not resolve SQLite candidate path." -ForegroundColor Yellow
    }
}

Write-Section "3) Running Backend process hints (not proof of DB file)"
$hints = Get-RunningHbiBackendHints
$backendProcessDetected = ($hints.Count -gt 0)
if ($hints.Count -eq 0) {
    Write-Host "No uvicorn app.main:app process found in this session query."
    Write-Host "Cannot prove from process list that a Backend is using this DB right now."
} else {
    foreach ($h in $hints) { Write-Host $h }
    Write-Host "Backend process command lines are inspected only in memory for matching and are never printed."
}

$activeProven = $false
$verdict = "UNKNOWN"

Write-Section "4) SQLite file audit (read-only) if path known"
if ($backendProcessDetected) {
    Write-Host "Backend process detected; skipping immutable SQLite inspection to avoid reading a changing live database." -ForegroundColor Yellow
    $verdict = "UNKNOWN"
} elseif ($kind -ne "SQLITE") {
    Write-Host "Non-SQLite database kind reported: $kind"
    Write-Host "This script does not open non-SQLite servers (by design)."
    Write-Host "Migration scripts for ProductProblemLink assessments are SQLite-specific on master."
    $verdict = "UNKNOWN"
} elseif (-not $sqlitePath) {
    Write-Host "SQLite path could not be resolved."
    $verdict = "UNKNOWN"
} elseif (-not (Test-Path -LiteralPath $sqlitePath)) {
    Write-Host "File does not exist: $sqlitePath" -ForegroundColor Yellow
    Write-Host "The audit candidate points here, but this does not establish the Backend runtime database."
    $verdict = "UNKNOWN"
} else {
    $item = Get-Item -LiteralPath $sqlitePath
    Write-Host "File exists: yes"
    Write-Host "Size bytes: $($item.Length)"
    Write-Host "Last write time (local): $($item.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"

    $audit = Invoke-SqliteReadonlyAudit -DbPath $sqlitePath
    if (-not $audit.Ok) {
        Write-Host "Read-only open failed: $($audit.Error)" -ForegroundColor Yellow
        $verdict = "UNKNOWN"
    } elseif (-not $audit.Data.ok) {
        Write-Host "SQLite report: $($audit.Data.error) $($audit.Data.detail)" -ForegroundColor Yellow
        $verdict = "UNKNOWN"
    } else {
        $d = $audit.Data
        Write-Host "integrity_check: $($d.integrity_check)"
        Write-Host "foreign_key_check violations: $($d.foreign_key_check_violations)"
        Write-Host "ProductProblemLink table: $($d.has_ProductProblemLink)"
        Write-Host "ProductProblemLinkAssessmentEvent table: $($d.has_ProductProblemLinkAssessmentEvent)"
        if ($d.has_ProductProblemLink) {
            Write-Host "ProductProblemLink columns:"
            Write-Host ("  " + ($d.ProductProblemLink_columns -join ", "))
            Write-Host "PR #496 new columns present:"
            $d.pr496_new_columns_present.PSObject.Properties | ForEach-Object {
                Write-Host ("  {0} = {1}" -f $_.Name, $_.Value)
            }
            Write-Host "ProductProblemLink row count: $($d.ProductProblemLink_row_count)"
        }
        if ($d.has_ProductProblemLinkAssessmentEvent) {
            Write-Host "ProductProblemLinkAssessmentEvent row count: $($d.ProductProblemLinkAssessmentEvent_row_count)"
        }
        Write-Host "Indexes/triggers on ProductProblemLink:"
        if ($d.ProductProblemLink_indexes_and_triggers.Count -eq 0) {
            Write-Host "  (none listed in sqlite_master)"
        } else {
            foreach ($it in $d.ProductProblemLink_indexes_and_triggers) {
                Write-Host ("  [{0}] {1}" -f $it.type, $it.name)
            }
        }

        $verdict = "READY_FOR_REVIEW"
        $activeProven = $false
    }
}

Write-Section "5) Other known candidate paths (NOT claimed active)"
$candidates = @(
    (Join-Path $repoRoot "data\hbi.db"),
    "E:\hbi\data\hbi.db",
    "E:\HBI_GitHub_Current\data\hbi.db",
    "C:\Users\F1\HBI_GitHub_Current\data\hbi.db"
) | Select-Object -Unique

foreach ($c in $candidates) {
    if ($sqlitePath -and ([System.IO.Path]::GetFullPath($c) -eq $sqlitePath)) {
        Write-Host "SKIP (same as effective path): $c"
        continue
    }
    if (Test-Path -LiteralPath $c) {
        $fi = Get-Item -LiteralPath $c
        Write-Host "EXISTS (candidate only): $c  size=$($fi.Length)  mtime=$($fi.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    } else {
        Write-Host "absent: $c"
    }
}
Write-Host "Candidates above are listed only for operator awareness. None is declared the active DB solely because it exists."

Write-Section "6) Verdict"
if (-not $activeProven) {
    Write-Host "ACTIVE_DB_PROOF = NOT_PROVEN" -ForegroundColor Yellow
    Write-Host "This script cannot prove that the inspected file is the one the running Backend holds open."
    Write-Host "If Backend is not running, or DATABASE_URL differs in another terminal/service, treat identity as UNKNOWN."
}
Write-Host "AUDIT_RESULT = $verdict"
Write-Host ""
Write-Host "Interpretation:"
Write-Host "  READY_FOR_REVIEW = file opened read-only and schema facts were collected; human still decides migration."
Write-Host "  UNKNOWN          = effective DB not established or file/schema could not be read."
Write-Host "  No migration was run. No temporary files or SQLite writes were performed."
Write-Host ""
Write-Host "Done."
exit 0
