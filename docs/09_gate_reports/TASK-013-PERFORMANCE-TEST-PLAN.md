# TASK-013 — HBI Performance Test Plan

| Field | Value |
|-------|--------|
| **Task** | TASK-013 |
| **Owner** | Grok1 |
| **Supervision** | ChatGPT |
| **Source of Truth** | `vahidmaghsoudi2/hbi` |
| **Document version** | 1.0 |
| **Date** | 2026-08-21 |
| **Constraint** | No Production code change; no existing test edits |

---

## 1. Goal

Provide a **repeatable** plan to measure whether HBI backend (API + Recommendation path) meets **MVP local** performance expectations before production-like deployment.

This Artifact is the **Plan only**. Execution results belong in a separate report file.

---

## 2. Performance scenarios

### S1 — Health / readiness
- Endpoint: health (or equivalent root health check used by ops)
- Load: sequential + light concurrent (see §4)

### S2 — Product list / verified products
- Read path only
- Dataset: seed or empty; **must record row counts**

### S3 — Evidence list by product
- Read path; Framework 3-related volume awareness

### S4 — Recommendation generate (critical path)
- Flow: Case + profile → `RecommendationService.generate_recommendations` → `ReasoningEngine.run`
- Measures end-to-end service latency on PO machine / CI, not public internet

### S5 — Reasoning engine isolated
- Direct `ReasoningEngine.run` with fixed synthetic inputs (N repeats)
- Separates scoring/reasoning cost from HTTP/ORM overhead

### S6 — Full automated regression wall-clock
- `pytest tests/` and `pytest tests/test_reasoning/` duration as **smoke performance** signal (not load test)

---

## 3. Metrics

| Metric | Definition |
|--------|------------|
| **Latency** | Time to complete one request/call (ms) |
| **p50 / p95** | 50th / 95th percentile over N samples |
| **Throughput** | Successful operations per second (ops/s) under fixed concurrency |
| **Error rate** | Failed requests / total |
| **Wall-clock suite** | Seconds for designated pytest paths |

**Not in MVP plan:** distributed tracing, GPU, multi-region.

---

## 4. Concurrent users (MVP definition)

| Level | Concurrent clients | Purpose |
|-------|-------------------|---------|
| L0 | 1 | Baseline latency |
| L1 | 5 | Light contention |
| L2 | 10 | Stress smoke for MVP |

> Gate 7 does **not** require 100+ virtual users. Higher levels need explicit PO/Qwen1 scope change.

---

## 5. Sensitive backend points

| Area | Why sensitive |
|------|----------------|
| `RecommendationService.generate_recommendations` | Loops products + inventory + engine |
| `ReasoningEngine.run` + `MatchScoringEngine` | CPU-bound scoring / conflict analysis |
| Evidence queries per product | ORM + filter cost grows with evidence rows |
| SQLite file DB on Windows | Locking / single-writer under concurrency |
| Auth/JWT paths | Extra crypto cost on protected routes |
| Facade DTO mapping | Extra queries (e.g. inventory lookups) |

---

## 6. PASS / FAIL criteria (MVP local)

| ID | Criterion | PASS | FAIL |
|----|-----------|------|------|
| C1 | Health p95 (L0) | ≤ 200 ms | > 200 ms |
| C2 | Product/Evidence list p95 (L0, small data) | ≤ 500 ms | > 500 ms |
| C3 | Recommendation generate p95 (L0, ≤20 products) | ≤ 2000 ms | > 2000 ms |
| C4 | ReasoningEngine.run p95 (N≥50 synthetic) | ≤ 50 ms | > 50 ms |
| C5 | Error rate (L1) | ≤ 1% | > 1% |
| C6 | `tests/test_reasoning/` wall | ≤ 5 s | > 5 s |
| C7 | Full `pytest tests/` wall (informative) | ≤ 60 s | > 60 s (YELLOW, not auto Gate fail) |

All runs must record: **git SHA**, machine, dataset size, timestamp.

---

## 7. Repeatable execution method

### Preferred
1. `git pull` → note SHA  
2. Optional Job via `agent-jobs/pending/*.json` + `hbi-agent-runner.ps1`  
3. Capture stdout to `agent-jobs/results/` or results markdown  
4. Publish results to GitHub  

### Commands (informative — execution is a later step)

```text
python -m pytest tests/test_reasoning/ -q
python -m pytest tests/ -q
```

### Future script (NOT created in this task)
Proposed only (needs approval before write):

```text
scripts/perf_baseline.py
```

Would: hit health/list with timing loop, call ReasoningEngine N times, print JSON summary.  
**No script file written under this Work Order without approval.**

---

## 8. Required Artifacts

| Artifact | Path |
|----------|------|
| Plan (this file) | `docs/09_gate_reports/TASK-013-PERFORMANCE-TEST-PLAN.md` |
| Results (later) | `docs/09_gate_reports/TASK-013-PERFORMANCE-RESULTS.md` |
| Optional job logs | `agent-jobs/results/*.log` |

---

## 9. Current gaps

- No published timing results yet on GitHub  
- No dedicated perf script yet (by design under this order)  
- Concurrent HTTP tooling (e.g. k6/locust) not in repo  
- Production-like multi-user DB not assumed  

---

## 10. Plan verdict

```text
PLAN STATUS: COMPLETE (design)
EXECUTION STATUS: NOT STARTED
PRODUCTION CODE CHANGED: NO
EXISTING TESTS CHANGED: NO
```
