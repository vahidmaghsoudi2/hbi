# HBI-PO-DEC-REC-SCOPE-001

**Decision ID:** `HBI-PO-DEC-REC-SCOPE-001`  
**Title:** Recommendation Policy Scope v1  
**Status:** **DECISION RESOLVED**  
**Date:** 2026-09-14  
**Authority:** Product Owner — Vahid Maghsoudi  
**Related:** Issue #37 — Recommendation Parameter Weighting  
**Implementation Authorization:** **NOT AUTHORIZED BY THIS DECISION ALONE**

---

## Decision

The Recommendation Policy v1 scope shall include the following three parameters:

1. **Need Match**
2. **Product Inventory**
3. **Evidence**

The following candidate parameters are **outside the Recommendation Policy v1 scope for now**:

4. **Product Ingredients**
5. **Seller / Operator Experience**

This decision is limited to **Scope** only.

It does **not** define or approve:

- Weight or Percentage
- Priority
- Gate
- Filter
- Signal
- Evidence definition beyond the scope term used here
- Combination formula
- UNKNOWN behavior
- CONFLICT behavior
- Validation method
- Policy version beyond this scope decision

### Mandatory separation

`Scope ≠ Role ≠ Weight ≠ Gate ≠ Filter ≠ Signal`

Membership in this Scope does not imply any particular role or numerical contribution.

---

## Decision Basis

The Decision 1 Runtime Reality Audit on `master` established:

- **Need Match:** active in the Recommendation path; Scope evidence was assessed as PARTIAL because explicit Policy-scope authorization was not found.
- **Product Inventory:** active in the Recommendation path and explicitly connected to Recommendation behavior by `HBI-PO-DEC-GAP03-001`.
- **Evidence:** active as an input to `evidence_score`; the distinction between general Evidence and Verified-only Evidence remains unresolved for later policy decisions.
- **Product Ingredients:** present as ProductKnowledge data/snapshot input, but independent Recommendation-policy participation was not evidenced.
- **Seller / Operator Experience:** no independent Recommendation parameter or scoring path was evidenced.

The PO decision resolves the Scope question based on the Reality Audit. It does not convert the existing Runtime into a weighting Policy.

---

## Authorization Boundary

| Action | Authorized by this record? |
|---|---|
| Documentation registration | **YES** |
| Treating the three in-scope parameters as Policy roles/weights | **NO** |
| Changing existing Recommendation Runtime | **NO** |
| Changing scoring weights | **NO** |
| Adding Ingredients or Seller/Operator Experience to Runtime | **NO** |
| Model / Migration / API / Runtime change | **NO** |
| Closing Issue #37 | **NO** |

---

## Next Decision

The next decision is **Decision 2 — Role** for the in-scope parameters:

- Need Match
- Product Inventory
- Evidence

Decision 2 shall determine whether and how each parameter functions as Weight, Gate, Filter, Signal, or Evidence, without assuming that the current Runtime role is the approved Policy role.

---

## Traceability

| Field | Value |
|---|---|
| Document ID | `HBI-PO-DEC-REC-SCOPE-001` |
| Related Issue | `#37` |
| Authority | PO Vahid Maghsoudi |
| Registration date | 2026-09-14 |
| Status | DECISION RESOLVED |
| Implementation | **NOT AUTHORIZED BY THIS DECISION ALONE** |

**END OF HBI-PO-DEC-REC-SCOPE-001**
