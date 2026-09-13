# HBI-PO-DEC-CORE-001

**Decision ID:** `HBI-PO-DEC-CORE-001`  
**Title:** HBI Core Definition v1  
**Status:** DECIDED / ACCEPTED  
**Decision Type:** Core Identity / Domain Definition  
**Scope:** HBI Core Discovery  
**Implementation Authorization:** NOT AUTHORIZED  
**Architecture Authorization:** NOT DEFINED BY THIS DECISION  
**GAP Status:** FROZEN  
**Source of Truth:** GitHub master  
**Date:** 2026-09-13  
**Authority:** Product Owner — Vahid Maghsoudi  
**Baseline master (at registration):** `eba5e5768df42d6505a2c5da33fa5ecb90dbd86e`  
**Version:** v1

---

## 1. Decision

The HBI Core is defined as:

> HBI یک سیستم Decision Support مسئله‌محور و Evidence-Bound است که واقعیت ناقص مشتری را در زمینه یک مسئله، با حفظ منشأ و وضعیت اعتبار اطلاعات، تفکیک Fact و Inference و مدیریت صریح Unknown و Conflict، به یک تصمیم قابل‌دفاع و قابل‌ردیابی تبدیل می‌کند؛ و در صورت کفایت تصمیم، از آن Need و سپس Recommendation استخراج می‌کند.

This definition establishes the current identity of HBI.

It does not prescribe a specific implementation architecture, entity model, database structure, API structure, or mandatory processing pipeline.

---

## 2. Core Identity Properties

The following four properties are considered defining characteristics of the HBI Core:

1. Problem-Centered  
2. Evidence-Bound  
3. Uncertainty / Conflict-Aware  
4. Decision-Oriented  

These are Core behavioral/domain properties, not implementation entities.

---

## 3. Explicit Boundary

The following distinction is mandatory:

```
Core Definition ≠ Architecture ≠ Entity Model ≠ Implementation Contract
```

The Core must not be interpreted as requiring the following fixed chain:

```
Customer → Case → Problem → Assessment → Factor → Evidence → Decision State → Need → Recommendation
```

The above may describe concepts or relationships identified during discovery, but this Decision does not mandate their existence, exact boundaries, persistence model, or implementation form.

---

## 4. Decision State

Decision State is recognized as an important intermediate representation within the current HBI reasoning process.

However:

**Decision State is not, by itself, the HBI Core.**

The HBI identity is the controlled, problem-centered, evidence-bound decision process and its governing behavioral properties.

---

## 5. What Is Not Core

The following are explicitly not defined as HBI Core by this Decision:

* Product Catalog  
* ProductKnowledge  
* Inventory  
* Accounting  
* Payment  
* UI / Frontend  
* Scoring / Ranking  
* Recommendation as an isolated capability  
* Recommendation Persistence as an isolated capability  
* FactorDefinition as an independent Entity  
* Feedback / Learning  
* Any specific Entity chain  

These components may be important supporting capabilities, but their existence does not define the identity of HBI.

---

## 6. Core Behavioral Boundaries

The following principles are part of the current Core definition:

* Unknown must not be converted into an unsupported Guess.  
* Conflict must not be silently treated as Fact.  
* Source must remain distinguishable from Validity.  
* Fact must remain distinguishable from Inference.  
* Insufficient evidence must be capable of limiting or preventing a definitive decision.  
* New information may change the current decision state.  
* Decision outputs must remain traceable to the information and reasoning that support them.  
* Recommendation is conditional on decision sufficiency and is not the definition of the Core itself.  

---

## 7. Core Discovery Evidence Basis

This Decision is based on the independent Core Discovery performed across the previously established HBI work, including:

* F0 Reality Audit  
* F1 work and findings  
* F2 architectural decisions and implementation  
* GAP-01 decision  
* GAP-02 Reality Audit  
* GAP-03 Reality Audit  
* GAP-04 decision  
* Current Repository / master reality  
* Independent outputs from Qwen and Grok team members  
* Independent management synthesis  

The independent outputs converged on the same central identity:

Problem-centered, evidence-bound decision support under uncertainty, leading to Need and, where justified, Recommendation.

A reported Qwen output contained repository paths inconsistent with the known Python/SQLAlchemy repository reality. Those specific repository claims were therefore not accepted as Evidence. The Core Candidate was evaluated separately against valid repository evidence and the converging independent findings.

---

## 8. Known Boundaries / Open Questions

This Decision does not resolve the following:

* Exact boundary between Problem, Assessment, Factor, Decision State and Need  
* Exact contents and persistence requirements of Decision State  
* Exact role of Case in the Core  
* Exact threshold for stopping a decision because of insufficient information  
* Exact effect of Medical Context on Decision State  
* Required depth of Decision → Need → Recommendation traceability  

These remain OPEN / UNKNOWN where not already resolved by a separate accepted decision.

They must not be silently converted into implementation requirements by this document.

---

## 9. Governance Boundary

This Decision:

* Does not authorize new Entities.  
* Does not authorize new database tables or migrations.  
* Does not authorize Refactor.  
* Does not authorize API changes.  
* Does not authorize changes to Recommendation Engine behavior.  
* Does not reopen frozen GAPs.  
* Does not authorize implementation of any capability merely because it appears in the Core definition.  

Any implementation work must pass through the established HBI governance process and receive the required authorization independently.

---

## 10. Core Test

For future architectural and design decisions, the following test shall be used:

> If this capability is removed, can HBI still remain the same kind of Problem-Centered, Evidence-Bound Decision Support system?

If yes, the capability should not automatically be classified as Core.  
If no, the capability may represent a Core behavioral property and requires explicit evaluation against this Decision.

This test is a decision-support criterion, not an automatic implementation rule.

---

## 11. Final Status

| Item | Status |
|------|--------|
| CORE DISCOVERY | CLOSED / DECIDED |
| HBI Core Definition v1 | ACCEPTED |
| Architecture | NOT DEFINED BY THIS DECISION |
| Implementation | NOT AUTHORIZED BY THIS DECISION |
| GAPs | FROZEN |

This Decision establishes the current HBI Core identity as the reference point for subsequent GAP, Contract, Design and Architecture work.

Any future change to the HBI Core definition requires an explicit new decision and must not be introduced implicitly through implementation.

---

**Product Owner:** Vahid Maghsoudi  
**Decision Authority:** Product Owner / HBI Project Governance  
**Decision Record:** HBI-PO-DEC-CORE-001  
**Version:** v1  
**Status:** DECIDED / ACCEPTED

**END OF HBI-PO-DEC-CORE-001**
