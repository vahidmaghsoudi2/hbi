# TASK-013 — Performance Testing Plan

| Field | Value |
|-------|--------|
| **Task** | TASK-013 |
| **Owner** | Grok1 (Hub A — Test / Red Team) |
| **Status** | IN_PROGRESS |
| **Phase** | Gate 7 |
| **Date** | 2026-08-21 |
| **Authority** | Qwen1 (execution) / PO (final) |
| **Source of Truth** | `vahidmaghsoudi2/hbi` |

## 1. Purpose

Define a **minimal, measurable** performance baseline for HBI before production-like use.

This document is the **first Artifact** for TASK-013.  
It is a **plan**, not a completed performance run.

## 2. Scope (IN)

| Area | What we measure |
|------|------------------|
| API health / list endpoints | Latency (p50/p95) under light load |
| Evidence list / product list | Response time |
| Reasoning path (unit) | Time for `ReasoningEngine.run` batch |
| Pytest suite wall-clock | Full `tests/` duration as regression signal |

## 3. Scope (OUT) — explicit NO ASSUMPTION

- Load testing thousands of concurrent users (not required for Gate 7 MVP)
- Production CDN / multi-region
- Products C & D identity work (PO locked UNIDENTIFIED)
- Changing scoring formulas for “speed”

## 4. Environment

| Item | Requirement |
|------|-------------|
| Code | `origin/master` only |
| DB | Prefer in-memory or local `data/hbi.db` from `init_db` + approved seed |
| Runner | Optional: `hbi-agent-runner.ps1` + Job under `agent-jobs/pending/` |
| Report | Must land in GitHub (`docs/09_gate_reports/` or `agent-jobs/results/`) |

## 5. Success criteria (MVP thresholds)

Draft thresholds (adjust only with Qwen1/PO):

| Metric | Target (MVP) |
|--------|----------------|
| `GET /health` (or equivalent) | p95 < 200 ms (local) |
| Lightweight list endpoint | p95 < 500 ms (local, small dataset) |
| `tests/test_reasoning/` | wall < 5 s |
| Full `pytest tests/` | wall < 60 s on PO laptop (informative) |

Failures against targets → YELLOW report, not silent pass.

## 6. Method

### Phase A — Baseline (this plan)
1. Record commit SHA under test
2. Record machine class (PO laptop / CI)
3. Run reasoning tests + full suite once; capture wall times

### Phase B — Micro-benchmarks
1. Script or pytest markers for repeated `ReasoningEngine.run` (N=50)
2. Optional: simple loop against TestClient health/list (N=20)

### Phase C — Report Artifact
Publish:

```text
docs/09_gate_reports/TASK-013-PERFORMANCE-RESULTS.md
```

Required fields: SHA, dates, raw timings, PASS/FAIL vs thresholds, limitations.

## 7. Execution path (preferred)

```text
Job JSON → agent-jobs/pending/
    → hbi-agent-runner.ps1 (PO online)
    → agent-jobs/results/*.log
    → (auto-publish if enabled) GitHub
```

Fallback: PO/DeepSeek runs commands; results committed under `docs/09_gate_reports/`.

## 8. Deliverables checklist

- [x] Performance **Plan** (this file)
- [ ] Baseline timing capture (commit SHA + wall times)
- [ ] Optional micro-benchmark script (only if approved; keep under `scripts/` or `tests/`)
- [ ] Results report on GitHub
- [ ] WORK-REGISTRY update to COMPLETED when Results verified

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Measuring only empty DB | State dataset size in report |
| Confusing unit test speed with production load | Label metrics clearly |
| Results only on laptop disk | Require GitHub Artifact |

## 10. Verdict on plan publication

```text
ARTIFACT: docs/09_gate_reports/TASK-013-PERFORMANCE-TEST-PLAN.md
OWNER: Grok1
STATUS: PLAN PUBLISHED — execution not yet complete
```
