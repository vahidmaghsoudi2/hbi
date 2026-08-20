#!/usr/bin/env bash
# hbi-test.sh — HBI Standard Test Runner (READ-ONLY friendly)
set -e
cd "$(dirname "$0")"

echo "========================================"
echo "HBI TEST EVIDENCE"
echo "========================================"
echo "Repository : vahidmaghsoudi2/hbi"
echo "Branch     : $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo N/A)"
echo "Commit     : $(git rev-parse HEAD 2>/dev/null || echo N/A)"
echo "Mode       : READ-ONLY"
echo "Timestamp  : $(date -Iseconds)"
echo ""

echo "[1/4] Dependency check..."
python3 -c "import pytest, sqlalchemy; print('deps OK')"

echo "[2/4] PyCompile..."
python3 -m py_compile app/services/recommendation_service.py
python3 -m py_compile app/reasoning/reasoning_engine.py
python3 -m py_compile app/reasoning/claim_validator.py
python3 -m py_compile app/reasoning/conflict_analyzer.py
python3 -m py_compile app/reasoning/scoring.py
echo "PyCompile: PASS"

echo "[3/4] Unit tests (reasoning)..."
if [ -d tests/test_reasoning ]; then
  python3 -m pytest tests/test_reasoning/ -v --tb=short
  echo "Reasoning tests: PASS"
else
  echo "tests/test_reasoning not found — skip"
fi

echo "[4/4] Full suite + Coverage..."
python3 -m pytest --cov=app --cov-report=term-missing -v

echo ""
echo "========================================"
echo "END OF HBI TEST EVIDENCE"
echo "========================================"
