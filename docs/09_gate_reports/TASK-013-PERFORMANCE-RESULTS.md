# TASK-013 — Performance Results (Phase A Baseline)

| Field | Value |
|-------|--------|
| **Task** | TASK-013 |
| **Owner** | Grok1 |
| **Supervision** | ChatGPT |
| **Phase** | A — Baseline |
| **Plan** | `docs/09_gate_reports/TASK-013-PERFORMANCE-TEST-PLAN.md` |
| **Code SHA under test** | `7e14f6005fc3870bb63760269fd8215fd3796755` |
| **Run UTC** | 2026-08-21T19:22:30Z |
| **Machine** | Linux sandbox (glibc 2.39), Python 3.12.3 — **not** PO Windows laptop |
| **Dataset** | Synthetic in-process for ReasoningEngine; pytest default fixtures (no production DB dump) |

---

## 1. Measurements performed

| Scenario | Measured? | Notes |
|----------|-----------|--------|
| S5 ReasoningEngine isolated | **YES** | N=50, `perf_counter` |
| S6 pytest `tests/test_reasoning/` | **YES** | wall + pytest internal |
| S6 full `pytest tests/` | **YES** | wall + outcome |
| S1–S4 HTTP API / Recommendation | **NO** | No live server load loop in this run; **NOT MEASURED** |

---

## 2. Raw results

### S5 — ReasoningEngine.run (N=50)

Inputs fixed: need_match=0.8, evidence_score=0.6, inventory_score=1.0, 1 FACT evidence item.

| Stat | ms |
|------|-----|
| min | 0.009 |
| p50 | 0.012 |
| p95 | 0.077 |
| max | 25.504 |
| mean | 0.578 |

### S6a — `pytest tests/test_reasoning/ -q`

| Field | Value |
|-------|--------|
| Exit | 0 |
| Pytest report | **38 passed in 0.19s** |
| Process wall | **3.073 s** (includes interpreter/import startup) |

### S6b — `pytest tests/ -q --tb=line`

| Field | Value |
|-------|--------|
| Exit | 1 |
| Pytest report | **100 passed, 1 warning, 1 error in 1.34s** |
| Process wall | **3.323 s** |
| Error | `tests/test_evidence.py::test_create_evidence_with_auth` |

---

## 3. Criteria evaluation (from Plan)

| ID | Criterion | Result | Verdict |
|----|-----------|--------|---------|
| C1 | Health p95 ≤ 200 ms | Not measured | **NOT MEASURED** |
| C2 | List p95 ≤ 500 ms | Not measured | **NOT MEASURED** |
| C3 | Recommendation p95 ≤ 2000 ms | Not measured | **NOT MEASURED** |
| C4 | ReasoningEngine p95 ≤ 50 ms | p95=0.077 ms | **PASS** |
| C5 | Error rate @L1 ≤ 1% | Not measured | **NOT MEASURED** |
| C6 | test_reasoning wall ≤ 5 s | 0.19s pytest / 3.07s process | **PASS** |
| C7 | full pytest ≤ 60 s (informative) | 1.34s pytest / 3.32s process but **1 ERROR** | **YELLOW** (time OK; suite not clean) |

---

## 4. Limitations (NO ASSUMPTION)

1. Environment is **Grok sandbox Linux**, not PO laptop — numbers are not interchangeable with Windows PO timings.
2. HTTP scenarios S1–S4 were **not** executed in Phase A.
3. Full suite has **1 error**; performance wall-clock alone must not be read as “all tests green”.
4. First-call max 25.5 ms on ReasoningEngine likely includes one-off warmup; p95 still well under C4.
5. No official GitHub Actions check attached to this results commit unless CI runs separately.

---

## 5. Phase A verdict

```text
PHASE A BASELINE: PARTIAL
C4, C6: PASS
C1–C3, C5: NOT MEASURED
C7: YELLOW (duration pass-ish; 1 test ERROR)
OVERALL PHASE A: YELLOW — plan criteria only partially evidenced
```

---

## 6. Next action

1. ChatGPT Reality Check on this Results Artifact  
2. Optional Phase B: HTTP latency on PO Runner (health/list/recommendation)  
3. DeepSeek: investigate `test_create_evidence_with_auth` error (outside pure perf scope)  
