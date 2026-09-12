# HBI-PO-DEC-GAP01-001

**Decision ID:** `HBI-PO-DEC-GAP01-001`  
**Type:** Product Owner Formal Decision — GAP Correction  
**Date:** 2026-09-12  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `5c9cd697dc00e55ee7dcde0186e53dc7e6a2f4d2`  
**Related:** F2 Implementation (PR #45) · Post-F2 Verification · GAP-01 Cross-Product Unknown Leakage  
**Status:** **DECISION RESOLVED — IMPLEMENTATION PENDING**

---

## Scope

This record registers the PO-approved contract for correcting GAP-01 (Cross-Product Unknown Leakage).

- Documentation registration only.
- **No Implementation authorization** is granted by this document.
- No Model / Migration / API / Runtime change is authorized until a subsequent explicit PO Implementation instruction.

---

## Decision — GAP-01 Minimal MVP Correction

### Approved Contract

1. **Case Decision State** remains shared and holds only Customer / Problem / Need-oriented information.

2. **Product Evaluation State** for the evaluation of each Product must be independent and **per-product**.

3. **Unknown / Conflict** belongs by default to the level at which it was discovered.

4. An Unknown / Conflict is elevated to Case level **only if** all of the following hold:
   - it is independent of any specific Product; **and**
   - its subject is Customer / Problem / Need / Safety; **and**
   - it can potentially affect more than one Product or the Decision State itself.

5. **Case-level examples:**
   - customer history of severe allergy
   - Unknown skin type
   - Unknown itch severity
   - Medical Context related to the customer
   - information independent of any Product that affects the overall decision

6. **Product-level examples:**
   - whether Product A contains a specific ingredient
   - insufficient Evidence for Product A
   - contraindication specific to Product A
   - conflict in Evidence belonging to Product A

7. **Product-level Unknown/Conflict must not mutate the shared Case Decision State.**

8. **Medical Context** remains a Case-level Decision Context under this decision and must not be turned into Diagnosis or Treatment.

---

## Authorization Boundary

| Action | Authorized by this record? |
|--------|----------------------------|
| Documentation registration of the above decision | **YES** |
| Implementation of the GAP-01 correction | **NO** — IMPLEMENTATION PENDING |
| Model / Migration / API / Runtime change | **NO** |
| Any further Contract finalization for coding | Requires subsequent explicit PO instruction |

---

## Traceability

| Field | Value |
|-------|--------|
| Document ID | HBI-PO-DEC-GAP01-001 |
| Baseline SHA | 5c9cd697dc00e55ee7dcde0186e53dc7e6a2f4d2 |
| Registration date | 2026-09-12 |
| Authority | PO Vahid Maghsoudi |
| Implementation status | **PENDING** |

**END OF HBI-PO-DEC-GAP01-001**
