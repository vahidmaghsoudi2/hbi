# hbi-test.ps1 — HBI Standard Test Runner
# Mode: READ-ONLY friendly (does NOT commit/push)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HBI TEST EVIDENCE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Repository : vahidmaghsoudi2/hbi"
try {
    Write-Host "Branch     : $(git rev-parse --abbrev-ref HEAD)"
    Write-Host "Commit     : $(git rev-parse HEAD)"
} catch {
    Write-Host "Branch/Commit: (git not available)"
}
Write-Host "Mode       : READ-ONLY"
Write-Host "Timestamp  : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

Write-Host "[1/4] Dependency check..." -ForegroundColor Yellow
python -c "import pytest, sqlalchemy; print('deps OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Install: pip install pytest pytest-cov SQLAlchemy" -ForegroundColor Red
    exit 1
}

Write-Host "[2/4] PyCompile..." -ForegroundColor Yellow
python -m py_compile app/services/recommendation_service.py
python -m py_compile app/reasoning/reasoning_engine.py
python -m py_compile app/reasoning/claim_validator.py
python -m py_compile app/reasoning/conflict_analyzer.py
python -m py_compile app/reasoning/scoring.py
Write-Host "PyCompile: PASS" -ForegroundColor Green

Write-Host "[3/4] Unit tests (reasoning)..." -ForegroundColor Yellow
if (Test-Path "tests/test_reasoning") {
    python -m pytest tests/test_reasoning/ -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "REASONING TESTS: FAIL" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "Reasoning tests: PASS" -ForegroundColor Green
} else {
    Write-Host "tests/test_reasoning not found — skip" -ForegroundColor Yellow
}

Write-Host "[4/4] Full suite + Coverage..." -ForegroundColor Yellow
python -m pytest --cov=app --cov-report=term-missing -v
$code = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "END OF HBI TEST EVIDENCE" -ForegroundColor Cyan
Write-Host "Exit code: $code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
exit $code
