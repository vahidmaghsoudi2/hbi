# HBI-PO-DEC-GAP02-001

**Decision ID:** `HBI-PO-DEC-GAP02-001`  
**Type:** Product Owner Formal Decision — GAP Resolution  
**Date:** 2026-09-13  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `cd56267f5270de3242978e2db1b85ade0990a30a`  
**Related:** HBI-PO-DEC-CORE-001 · HBI-PO-DEC-F2-ARCH-001 · GAP-02 Reality Audit  
**Status:** **DECISION RESOLVED**

---

## Scope

This record registers the PO-approved resolution of GAP-02 (Factor vs Concern).

- Documentation registration only.
- **No Implementation authorization** is granted by this document.
- No Model / Migration / API / Runtime change is authorized.

---

## Decision — GAP-02 Factor vs Concern (MVP)

1. **Factor** is a **Domain Concept**: any piece of information that participates in the decision about a problem, with explicit Source and Validity.

2. **Concern** is **raw customer input**. Concern is not automatically a Factor.

3. In MVP, Factor may be represented as a **computed item inside Decision State** (in-memory).  
   **FactorDefinition Entity** and **CaseFactor Table** are **NOT REQUIRED FOR MVP**.

4. This resolution is compatible with `HBI-PO-DEC-CORE-001` (FactorDefinition as independent Entity is Not Core) and with the existing Runtime representation in Decision State.

5. No code, migration, or runtime change is authorized by this decision.

---

## Authorization Boundary

| Action | Authorized by this record? |
|--------|----------------------------|
| Documentation registration | **YES** |
| Creation of FactorDefinition / CaseFactor Entity | **NO** |
| Model / Migration / API / Runtime change | **NO** |
| Reopening of this GAP | **NO** — RESOLVED |

---

## Traceability

| Field | Value |
|-------|--------|
| Document ID | HBI-PO-DEC-GAP02-001 |
| Baseline SHA | cd56267f5270de3242978e2db1b85ade0990a30a |
| Registration date | 2026-09-13 |
| Authority | PO Vahid Maghsoudi |
| Status | DECISION RESOLVED |

**END OF HBI-PO-DEC-GAP02-001**
