# HBI-PO-DEC-GAP04-002

**Decision ID:** `HBI-PO-DEC-GAP04-002`  
**Title:** GAP-04 Option B — Current Recommendation Uniqueness  
**Status:** **DECISION RESOLVED**  
**Date:** 2026-09-13  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `b88bfbcb7e6ada0656bd5caf8c58fd7c4ce534b3`  
**Related:** HBI-PO-DEC-GAP04-001 (Persistence) · GAP-04 Reality Audit  
**Implementation Authorization:** **NOT AUTHORIZED BY THIS DECISION ALONE**

---

## Scope

This record registers the PO-accepted **Option B** Contract for Current Recommendation Persistence behavior.

It **extends** `HBI-PO-DEC-GAP04-001` (Recommendation must persist + be traceable to Case/Decision).

- Documentation registration only.
- No Implementation authorization is granted.
- No Model / Migration / API / Runtime change is authorized.

---

## Contract Decision (Option B — ACCEPTED)

For each **Case + Product** pair, there is **at most one current Recommendation**.

- A subsequent Generate for the same Case + Product **must not** create an independent, duplicate Recommendation.
- Generate **updates / replaces** the existing current Recommendation with the new result.

### Boundary of this Decision

| In scope | Out of scope |
|----------|--------------|
| Current Recommendation Persistence | Historical Snapshot |
| Uniqueness of current Recommendation per Case + Product | Recommendation History / Audit Trail |
| Update-or-replace on re-Generate | Feedback / Learning |

If Historical Snapshot or Audit Trail is required later, it must be addressed in a **separate** GAP / Contract / Design.

---

## Relation to HBI-PO-DEC-GAP04-001

| Topic | GAP04-001 | GAP04-002 (this) |
|-------|-----------|------------------|
| Persist Recommendation | Required | Affirmed |
| Traceability to Case/Decision | Required | Affirmed |
| Uniqueness (one current per Case+Product) | Not specified | **Required** |
| Re-Generate behavior | Not specified | **Update/Replace** |
| History | Out of scope | Out of scope |

No conflict with GAP04-001. This Decision completes the Current Recommendation Contract.

---

## Authorization Boundary

| Action | Authorized by this record? |
|--------|----------------------------|
| Documentation registration | **YES** |
| Implementation of Persistence + Uniqueness | **NO** — requires separate explicit PO Implementation authorization |
| Model / Migration / API / Runtime change | **NO** |
| Historical Snapshot / Audit Trail | **NO** — out of scope |

---

## Status

| Item | Status |
|------|--------|
| Contract Registered | **YES** (pending Merge to master) |
| Implementation | **NOT AUTHORIZED** |
| Conflict with existing GAP04-001 | **NONE** |

---

## Traceability

| Field | Value |
|-------|--------|
| Document ID | HBI-PO-DEC-GAP04-002 |
| Baseline SHA | b88bfbcb7e6ada0656bd5caf8c58fd7c4ce534b3 |
| Registration date | 2026-09-13 |
| Authority | PO Vahid Maghsoudi |
| Status | DECISION RESOLVED |
| Implementation | NOT AUTHORIZED |

**END OF HBI-PO-DEC-GAP04-002**
