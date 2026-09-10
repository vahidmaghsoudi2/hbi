# HBI-PO-DEC-F2-ARCH-001

**Decision ID:** `HBI-PO-DEC-F2-ARCH-001`  
**Type:** Product Owner Formal Architectural Decisions (F2)  
**Date:** 2026-09-10  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `b103672bc50b1b89c21dd99e24076a2d6d2d616d`  
**Related:** F0/F1 Reality Audit CLOSED · F2 Contract phase  
**Status:** REGISTERED (documentation only)

---

## Scope

This record registers the F2 architectural decisions that are **CLOSED** by PO.

- No Implementation authorization is granted by this document.
- No Model / Migration / API / Runtime change is authorized.
- No new Contract is finalized for implementation without a subsequent explicit PO instruction.

---

## 1. Decision State

**Decision:** Decision State is an independent Domain Concept.

- In MVP it is **not** required to be a heavy independent database Entity.
- Decision State ≠ Case ≠ Recommendation ≠ Diagnosis.

**Implication:** Decision State holds the current decision-relevant snapshot of a Case (Assessment, Factors, Evidence validity, Unknowns, Conflicts, inferred Needs). Ownership and persistence form remain open for Implementation Design; the concept itself is accepted.

---

## 2. Unknown — Three Levels

**Decision:** Unknown has exactly three levels:

| Level | Behaviour |
|-------|-----------|
| **CRITICAL_UNKNOWN** | Stop decision / force Next Question |
| **IMPORTANT_UNKNOWN** | Limited decision + reduced Confidence |
| **OPTIONAL_UNKNOWN** | Continue decision with explicit Caveat |

**Hard rule:** Unknown is **never** filled by guesswork or invented data.

---

## 3. Medical Context

**Decision:** Medical Context is a **Decision Context**.

- When it affects the decision it **must** enter Reasoning.
- Medical Context ≠ Diagnosis ≠ Treatment.

---

## 4. Need

**Decision:** Need is produced from Decision State:

```
Decision State → Need Generation → Need
```

- Need is **not** determined directly from Customer Input or from Product.
- Need sits **before** Product Requirement.

---

## 5. Factor

**Decision:**

- **FactorDefinition** = general definition of a Factor in the Knowledge Domain.
- **CaseFactor** = the state of that Factor inside a specific Case.

```
FactorDefinition → CaseFactor
```

---

## 6. Standing Principle (re-confirmed)

```
Source / Origin
      ≠
Validity / Truth Status
      ≠
Inference
```

This separation remains mandatory for all Decision State content.

---

## Authorization Boundary

| Action | Authorized by this record? |
|--------|----------------------------|
| Documentation registration of the above decisions | **YES** |
| Implementation / Model / Migration / API / Runtime change | **NO** |
| Finalization of any new Contract for coding | **NO** — requires subsequent explicit PO instruction |
| Merge of this documentation record | Pending PO merge authorization |

---

## Traceability

| Field | Value |
|-------|--------|
| Document ID | HBI-PO-DEC-F2-ARCH-001 |
| Baseline SHA | b103672bc50b1b89c21dd99e24076a2d6d2d616d |
| Registration date | 2026-09-10 |
| Authority | PO Vahid Maghsoudi |

**END OF HBI-PO-DEC-F2-ARCH-001**
