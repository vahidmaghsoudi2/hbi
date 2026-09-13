# HBI-PO-DEC-GAP03-001

**Decision ID:** `HBI-PO-DEC-GAP03-001`  
**Title:** Out-of-Stock Candidate Elimination Policy  
**Status:** **DECISION RESOLVED**  
**Date:** 2026-09-13  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `0e0f112996895a7abde81f145c8d293848501306`  
**Related:** Post-F2 Verification · GAP-03 Reality Audit  
**Implementation Authorization:** **NOT AUTHORIZED BY THIS DECISION ALONE**

---

## Policy

A product with **Inventory = 0** shall be **eliminated from the Recommendation candidate set before Reasoning and Ranking**.

```
Inventory = 0
      ↓
Candidate Elimination
      ↓
No Reasoning
      ↓
No Ranking
      ↓
No Recommendation Object
```

### Rationale

An unavailable product is not currently actionable as a recommendation.  
Therefore it must not enter downstream Reasoning or Ranking.

---

## Current Runtime (FACT)

The current implementation applies an Inventory Hard Gate **after** the product enters the reasoning pipeline (inventory_score = 0 → hard-gate inside MatchScoringEngine / eligibility mapping).  
Recommendation objects may still be created.

This Decision defines the **required future behavior**; it does not change Runtime by itself.

---

## Required Future Behavior

- Inventory = 0 → Candidate Elimination  
- No Reasoning  
- No Ranking  
- No Recommendation object  

---

## Authorization Boundary

| Action | Authorized by this record? |
|--------|----------------------------|
| Documentation registration | **YES** |
| Implementation of elimination-before-reasoning | **NO** — requires separate explicit PO Implementation authorization |
| Model / Migration / API / Runtime change | **NO** |
| Reopening of this Decision | **NO** — RESOLVED |

---

## Status Summary

| Item | Status |
|------|--------|
| Reality Audit GAP-03 | Done |
| Policy | RESOLVED — Elimination before Reasoning |
| Runtime current | Hard Gate after entry into Reasoning |
| Implementation | **PENDING AUTHORIZATION** |
| Migration / Refactor / PR | **NOT AUTHORIZED** |

---

## Traceability

| Field | Value |
|-------|--------|
| Document ID | HBI-PO-DEC-GAP03-001 |
| Baseline SHA | 0e0f112996895a7abde81f145c8d293848501306 |
| Registration date | 2026-09-13 |
| Authority | PO Vahid Maghsoudi |
| Status | DECISION RESOLVED |
| Implementation | PENDING AUTHORIZATION |

**END OF HBI-PO-DEC-GAP03-001**
