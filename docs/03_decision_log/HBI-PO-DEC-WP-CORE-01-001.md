# HBI-PO-DEC-WP-CORE-01-001

**Decision ID:** `HBI-PO-DEC-WP-CORE-01-001`  
**Type:** Product Owner Formal Decision (governance record)  
**Date:** 2026-09-09  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at record):** `90788e854e8205c1493f2dd41d876a1521f20fa7`  
**Related Roadmap:** `HBI-ROADMAP-CORE-001`  
**Related Ledger:** `HBI-LEDGER-EXEC-001`

---

## Decision

| Item | Official status |
|------|-----------------|
| **WP** | **WP-CORE-01** |
| **Domain Contract v1** | **PO ACCEPTED** |
| **Implementation** | **NOT AUTHORIZED** |
| **Model / Migration / API / DTO / DB changes** | **NOT AUTHORIZED** |
| **Recommendation / Scoring / Weighting / Ranking / Eligibility** | **Out of scope of this WP** |
| **Next Authorized Step** | **Implementation Design only** (no code) |

---

## Critical governance separation

```
PO ACCEPTED (Domain Contract)
        ≠
Implementation Authorized
```

Acceptance of the Domain Contract **does not** authorize:

- production code
- schema / migration
- API or DTO changes
- database changes
- scoring / ranking / eligibility work

Implementation may begin **only after**:

1. Implementation Design completed (with Reality Audit on current master)
2. Explicit **PO Authorization** for Implementation

---

## Next Authorized Step — Implementation Design (no code)

Before any code, a **fresh Reality Audit on current master** is required, then delivery of:

1. Precise Model and relationships design  
2. Impact on existing models  
3. Impact Map  
4. Migration strategy and data integrity  
5. API / DTO design if needed  
6. Test and Regression plan  
7. Self-Critique  
8. Items requiring PO decision  

Output of Implementation Design must be submitted for **PO Authorization**.  
Only after that authorization may Implementation start.

---

## Reality note (registration time)

- This record registers the **PO decision status**.  
- A file path for “Domain Contract v1” body was **not** verified as present on master at baseline `90788e85…` during this registration pass.  
- Locating or landing the Contract text on master is a separate documentation action if still missing; **PO ACCEPTED status is recorded here regardless** as the formal decision event.

---

## Status labels (must not be collapsed)

| Label | Meaning for WP-CORE-01 |
|--------|-------------------------|
| PO ACCEPTED | Domain Contract v1 accepted by PO |
| NOT AUTHORIZED | Implementation and related technical changes |
| Next | Implementation Design (docs only) |

**END OF HBI-PO-DEC-WP-CORE-01-001**
