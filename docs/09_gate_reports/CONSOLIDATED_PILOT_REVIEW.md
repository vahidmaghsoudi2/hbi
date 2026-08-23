# CONSOLIDATED PILOT REVIEW

**Integrator:** Grok1  
**Master at consolidation:** `905106784f28e5ab2ac3c873fc3ac173d6336368`  
**CI on that HEAD:** [run 32660377449](https://github.com/vahidmaghsoudi2/hbi/actions/runs/32660377449) — **success**  
**Backend pilot path CI:** `245aefd3377e7ad386c16f641988dab917a8e5c0` — success (run 32654254906)

```text
Review reports = INPUTS, not SoT
UNKNOWN ≠ BLOCKER
Product A–D FROZEN — no product/seed/threshold changes in this package
```

---

## 0. Review Inbox status

| Input | Path | Raw body in GitHub |
|-------|------|---------------------|
| Qwen1 Failure/QA | docs/08_review_inbox/HBI_QWEN1_FAILURE_AUDIT.md | **Absent** — slot only |
| Qwen2 Evidence Arch | docs/08_review_inbox/HBI_QWEN2_EVIDENCE_ARCH_AUDIT.md | **Absent** — slot only |
| DeepSeek1 Security | docs/08_review_inbox/HBI_DEEPSEEK1_SECURITY_AUDIT.md | **Absent** — slot only |
| DeepSeek2 Pilot UX | docs/08_review_inbox/HBI_DEEPSEEK2_PILOT_UX_AUDIT.md | **Absent** — slot only |

Material verification performed against **actual master files**, not reviewer prose.

---

## 1. VERIFIED PASS

| Finding | Repository Evidence | PILOT BLOCKER |
|---------|---------------------|---------------|
| Auth required on recommendation generate | `app/api/routers/recommendations.py` — `Depends(get_current_customer_id)` | NO |
| Case ownership enforced | `_assert_case_owned` → 403/404 | NO |
| Missing/invalid token → 401 | `app/core/deps.py` `get_current_customer_id` | NO |
| Login OTP not implemented (expected) | `auth.py` `/login` → 501 POD-001 | NO (Version Next) |
| pilot-token disabled when HBI_ENV=production | `auth.py` → 403 | NO if Pilot uses non-production |
| get_db commits on success | `app/database.py` commit/rollback | NO |
| get_db single re-export | `app/core/deps.py` | NO |
| Product freeze + ops readiness docs | WORK-REGISTRY; HBI_FINAL_OPERATIONS_READINESS.md | NO |
| CI green on current docs HEAD | Actions 32660377449 success | NO |
| CI green on pilot backend SHA | Actions 32654254906 success | NO |
| Record-sourced ledger exists | docs/03_evidence_ledger/ISDIN_PRODUCTS_A_B_C_D_LEDGER.md | NO |
| UI not required for API Pilot | no UI in critical path; order allows optional | NO |

---

## 2. VERIFIED DEFECT

**NONE** requiring code change for Phase-1 Pilot start (no stop-ship defect verified against master).

---

## 3. HIGH RISK (not automatic Pilot blockers)

| Item | Evidence | PILOT BLOCKER |
|------|----------|---------------|
| pilot-token issues JWT for any existing customer_id in non-production | `auth.py` `/pilot-token` | NO for controlled Pilot; YES if mis-deployed as production without HBI_ENV |
| Default HBI_ENV is development | `os.getenv("HBI_ENV", "development")` | NO if ops sets production correctly |
| Intermediate CI failures on mid-pilot commits | runs 32654194275, 32654239482 failed; fixed by 245aefd3 | NO — HEAD lineage green |

---

## 4. UNKNOWN REQUIRING VERIFICATION

| Item | Why |
|------|-----|
| Exact Qwen1/Qwen2/DeepSeek narrative findings | Raw reports not in GitHub |
| Every failure-mode test coverage matrix (duplicate request, malformed body, empty product set) | Not exhaustively proven from file read alone without test run logs per case |
| Runtime EVIDENCE_MISSING string in service (code search incomplete) | Gate documented in commits/tests lineage; string not confirmed via search API |

UNKNOWN ≠ BLOCKER.

---

## 5. OPTIONAL / VERSION NEXT

- OTP / Magic Link (POD-001)
- Full UI
- REGULATORY evidence campaigns
- Unfreeze Product A–D
- barcode_gtin collection
- Production secrets hardening beyond HBI_ENV gate

---

## 6. REAL PILOT BLOCKERS

**NONE** verified on master `90510678…` with green CI.

Process only: explicit **PO Pilot Start** decision (and optional auditor note).

---

## 7. MINIMAL REQUIRED FIXES

**NONE** for code.  
Optional ops condition: set `HBI_ENV=production` on any non-pilot deployment so `/pilot-token` returns 403.

---

## 8. FINAL PILOT STATUS

```text
READY WITH CONDITIONS
```

Conditions:
1. PO accepts Phase-1 scope (pilot-token + EVIDENCE_MISSING hard-gate + frozen A–D).
2. Non-pilot environments set `HBI_ENV=production`.
3. External review bodies may be pasted into inbox later without changing this verdict unless new **verified** stop-ship appears.

No code changes in this consolidation commit.
