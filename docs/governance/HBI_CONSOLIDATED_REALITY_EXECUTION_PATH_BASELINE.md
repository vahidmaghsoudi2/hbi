# HBI — CONSOLIDATED REALITY & EXECUTION PATH BASELINE

## 0. Status and Authority of This Document

**Document role:** Management Baseline / WP-0 Reference

This document is **not the technical source of truth** and does not itself establish Repository Reality, Business Truth, or Operational Reality.

The authority order is:

```
CURRENT MASTER REALITY
→ EVIDENCE
→ ACCEPTED V1 SEMANTICS
→ DELTA
→ DECISION
→ AUTHORIZATION
→ IMPLEMENTATION
→ VERIFICATION
```

Therefore:

- This document records the current management understanding and execution route.
- A statement in this document does **not** become technical reality merely because it is written here.
- If exact inspection of Master contradicts this document, **Current Master Reality + Evidence wins** and this document must be corrected.
- If a business semantic is not traceable to an authoritative accepted artifact, it must remain **OPEN / UNPROVEN**, not be promoted to accepted truth.
- PR #315 is the registration vehicle for this baseline; it is not itself a technical truth source and is not an implementation authorization.
- Commit `aced20a2a8f5278519f3792905069a42780241a1` is the content currently registered on PR #315; it is not the final truth after merge.
- Master baseline `a05e1708d24e2485c5f6307f8f85b2c676b6017d` is the repository baseline from which this registration was prepared.

## Purpose

This document provides one consolidated management map for the HBI execution path and prevents drift between historical proposals, repository capability, accepted business semantics, agent reports, and operational reality.

It is a **management map**, not an implementation specification and not a substitute for repository evidence.

## Current Governance State

- Repository: `vahidmaghsoudi2/hbi`
- Master baseline used for registration: `a05e1708d24e2485c5f6307f8f85b2c676b6017d`
- PR #315: **OPEN / NOT MERGED**
- WP-0 — Recommendation Reality Map: **IN PROGRESS**
- GPT-2 Reality Audit: **IN PROGRESS / classification correction required**
- GPT-1 Independent Verification: **WAITING for corrected WP-0**
- Implementation: **NOT AUTHORIZED**
- Architecture / Schema / API / Recommendation / Scoring changes: **NOT AUTHORIZED**

## HBI Truth Model

```
Repository Capability ≠ Business Truth ≠ Operational Reality
```

Also:

- Agent Report ≠ Reality
- Missing Component ≠ Proven Business Gap
- Repository Artifact ≠ Customer Data
- Historical Proposal ≠ Accepted Business Contract
- Test Fixture ≠ Real Operational Data

Evidence chain:

```
Repository File → Symbol / Behavior → Exact Commit SHA → Test → CI → Runtime Evidence
```

## Status Vocabulary

- **PROVEN** — directly supported by evidence.
- **PARTIAL** — some behavior is proven, but the full claim is not.
- **UNPROVEN** — evidence is insufficient.
- **MISSING** — repository capability is absent.
- **OPEN** — business/semantic requirement is not authoritatively decided.
- **BLOCKED** — a required gate prevents legitimate progression.

A repository limitation is not automatically a business gap.

The comparison is:

```
Current Repository Reality
+
Accepted Business Semantics
=
Delta
```

## 1. Problem Space and Problem Bank

Discovery expanded to **P01–P61**, organized through **Skin Problem Space Map V0.1**.

The Map is organizational/observational, not a hidden medical taxonomy.

Established semantic boundaries:

- Problem ≠ Need
- Presentation / Manifestation ≠ Underlying Condition
- Clinical Condition ≠ Canonical HBI Problem
- Subtype ≠ Severity
- Medical existence ≠ HBI relevance
- Safety/referral classification ≠ operational referral protocol

Current management state:

- Skin Problem Space Map V0.1: **ACCEPTED / FROZEN**
- Problem Bank V1: **ACCEPTED WITH CONDITIONS**
- Problem Bank implementation: **NOT AUTHORIZED**

Known open items include P08 canonical-status strength, HBI Relevance admission criterion, and S01/S02 direct artifact inspection. These were not treated as blockers for pre-pilot readiness.

Problem Bank V1 is sufficient for the next controlled stage, but is not claimed to be field-validated or complete.

These statements remain management records and must yield to exact repository evidence if contradicted.

## 2. Problem → Need Contract

Current baseline:

```
docs/contracts/problem-need/PROBLEM_NEED_CONTRACT_V0.1.1.md
```

- Commit: `5ea25188d3cffbe3ebf286e80cae7de30643c475`
- Blob: `b0db2d0fd0ef03d499caaeb131c63c16c4ce8e83`
- Base: `a05e1708d24e2485c5f6307f8f85b2c676b6017d`
- Management status: **BASELINED — ACCEPTED WITH CONDITIONS**

Boundary:

```
Problem ≠ Need ≠ Diagnosis ≠ Product ≠ Recommendation
```

Need outcomes:

- ELIGIBLE
- PENDING
- NOT DETERMINABLE

A Problem label alone does not authorize a Need. Need eligibility is case-specific and requires recorded consultation evidence beyond the Problem label.

Need Bank V1 is not currently treated as a fully accepted final bank.

Where an accepted semantic is asserted here, future WP-0 verification must still trace it to the authoritative artifact before treating it as technical truth.

## 3. Customer / Consultation

The repository has an established Customer / Case / Consultation Context path and recommendation-related capabilities.

Previously recorded milestones:

- Consultation vertical slice: PR #215, accepted at `032e14ad031007616dfea6c678a559bf2f48c040`
- Bounded Skin Next Question: PR #226, accepted at `a8f7c941496eb4ee5d1f5e64be2233763f1f2377`
- Customer Profile V1.1: PR #190, approved at `8bd7af6e9cf121f4569ebb0ba6782d61c2f00390`

These are historical management references in this baseline; exact current Master behavior must be verified before a present-tense technical claim is made.

The five Customer Profile boxes are a UI projection, not a five-entity data model.

No recommendation/scoring/evidence-gate change follows from Customer Profile V1.1 unless an authoritative later decision says otherwise.

## 4. Customer Reality

HBI has not yet been established as operating with normal real customer use in the current evidence record.

Therefore this baseline does not promote customer reality or customer language to verified technical/operational truth.

- Customer Reality: **NOT VERIFIED**
- Customer Language: **NOT VERIFIED**
- Synthetic examples cannot become customer evidence.
- Repository artifacts cannot be reclassified as customer data.

The future gate is controlled acquisition of traceable real customer-originated evidence.

## 5. Product / Product Knowledge

The management map recognizes an existing Product/Product Knowledge path involving product identity/lifecycle, intake, knowledge, evidence, QA, compatibility/reasoning, and inventory-related eligibility.

Broad lifecycle recorded in project history:

```
Introduce → Duplicate → Research Draft → Enrich → Evidence / QA
→ PO Review → Approve → Activate → Inventory → Recommendation
```

This lifecycle is a management reference. Exact current repository capability must be established by WP-0 evidence.

Real Product Pilot remains an operational area requiring verification.

## 6. Recommendation — Management Map of Current Path

The path currently being audited is:

```
Customer / Case / Consultation Context
→ Need Normalization
→ Candidate Universe
→ Product Knowledge Compatibility / Relation
→ Eligibility
→ Customer Context
→ Existing Scoring
→ Ranking
→ Recommendation + Explanation / Trace
→ Operator Decision / Override
→ Outcome
```

**Important:** this is the management map of the path under audit. It is not proof that every arrow currently exists, is connected, or has the stated business meaning.

## 7. WP-0 Recommendation Reality Map

Mandatory audit stages:

```
Customer Input
→ Canonical Need
→ Gallery / Candidate Universe
→ Relation
→ Eligibility
→ Customer Fit
→ Scoring
→ Ranking
→ Explanation / Evidence
→ Operator Decision
```

For every stage, WP-0 must separately establish:

1. Current Master repository capability
2. Operational Reality
3. Exact evidence
4. Status
5. Authoritative accepted business meaning
6. Delta
7. Blocking?
8. Minimum next action

Required table:

| Stage | Current Master Repository Capability | Operational Reality | Evidence | Status | Accepted Semantics | Delta | Blocking? | Minimum Next Action |
|---|---|---|---|---|---|---|---|---|
| Customer Input | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Canonical Need | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Candidate Universe | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Relation | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Eligibility | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Customer Fit | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Scoring | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Ranking | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Explanation / Evidence | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |
| Operator Decision | verify | verify separately | exact | status | authoritative source | delta | yes/no | minimum |

WP-0 identifies reality and deltas. It does not redesign architecture.

## 8. Candidate Universe

Candidate Universe must be examined **before** Relation and Eligibility.

Key question:

> Which products enter the candidate set, and why?

Candidate formation, Relation, Eligibility, and Ranking must remain separate concepts.

A previously reported repository behavior includes gates involving:

```
Identity Verified + Active + QA Valid + Inventory > 0
```

For this baseline, that statement is classified as **reported repository behavior requiring exact WP-0 verification**, not as final technical truth or business contract.

## 9. Relation / Compatibility

A previously reported repository capability includes ProductKnowledge-driven compatibility/use-case matching into canonical Need IDs and a need-match signal.

Current classification in this management baseline:

- Compatibility mechanism: **reported capability; exact current-Master verification required**
- Independent Relation state such as `RELATED / NOT_RELATED / UNKNOWN`: **not established by this document**
- Requirement for an independent Relation state: **OPEN until traced to authoritative business semantics**

Missing a component does not authorize building it.

## 10. Eligibility

Eligibility is part of the Recommendation behavior being audited.

The reported gates are:

```
Identity Verified + Active + QA Valid + Inventory > 0
```

For this baseline they are **not promoted to final technical truth** until WP-0 verifies exact file/symbol/behavior/test evidence.

Boundary:

```
Eligibility ≠ Ranking
```

## 11. Customer Fit

Customer / Case / Consultation Context and ProfileFact-related capabilities have been reported as sources of customer context.

No independent standalone Customer Fit Engine is established by this document.

Classification:

- Customer context capability: **to be verified on current Master**
- Independent Fit Engine: **not established**
- Requirement for a separate Fit Engine: **OPEN** unless an authoritative business artifact requires it

No Fit Engine should be built merely because the code does not use that name.

## 12. Scoring

Previously recorded scoring behavior:

- Need: **0.50**
- Evidence: **0.30**
- Inventory: **0.20**

This is a historical repository claim carried into WP-0 for verification.

Scoring is **NOT AUTHORIZED FOR REDESIGN**.

## 13. Ranking

Previously recorded ranking behavior orders eligible candidates by ranking score.

The governing conceptual boundary is:

```
Ranking orders.
Eligibility excludes.
```

The following are management-level intended semantics and require exact verification before being called current repository behavior:

- backend result set remains complete for eligible results
- UI may initially show up to five
- Show More exposes additional results
- operator remains final decision-maker

## 14. Explanation / Evidence / Trust Trace

Recommendation explanation and trace capabilities have been reported, including evidence references and Trust Trace.

A reported current limitation is that products excluded before a Recommendation record exists do not necessarily receive a full persisted why-not trace.

This is retained as a **question for WP-0 verification**, not as an unqualified present-tense repository fact.

Whether full exclusion observability is a V1 business requirement is **OPEN** unless tied to an authoritative acceptance criterion.

## 15. Operator Decision

The governing business boundary recorded in project decisions is:

```
Recommendation ≠ Decision
```

The intended model is decision support: the operator can inspect reasons, evidence, warnings and update needs and makes the final selection/decision.

Previously reported specialist/operator override behavior includes ACCEPT / REJECT / MODIFY_SELECTION.

Exact current implementation must be verified from Master before being treated as current technical reality.

## 16. End-to-End Direction

Management target path:

```
CUSTOMER REALITY
↓
Problem / Presentation
↓
Need
↓
Consultation Context
↓
Candidate Universe
↓
Relation / Compatibility
↓
Eligibility
↓
Customer Fit
↓
Scoring
↓
Ranking
↓
Explanation / Evidence / Trust Trace
↓
Operator Decision
↓
Outcome / Follow-up
↓
Controlled Pilot
↓
Operational Reality
```

This is a **targeted audit/execution map**, not proof that every arrow is currently implemented or operational.

WP-0 determines the exact status of each arrow.

## 17. Five Controlled Questions — Not Five Proven Gaps

1. **Candidate Universe:** What exactly constitutes the candidate set, and is current Master formation aligned with accepted semantics?
2. **Relation:** Is current compatibility/use-case matching sufficient, or is an explicit Relation boundary actually required?
3. **Customer Fit:** What exactly does Customer Fit mean, and is current customer-context consumption sufficient?
4. **Exclusion Observability:** Which exclusions must be explainable/auditable, and to what level?
5. **Operational Reality:** Which capabilities have actually been exercised in real HBI operation?

These are controlled questions, not proven gaps.

No question becomes a build requirement without an evidence-backed business/contract decision.

## 18. Execution Route

### Step 1 — Close WP-0
GPT-2 completes the corrected Recommendation Reality Map from current Master evidence.

### Step 2 — Independent Verification
GPT-1 independently checks:

```
Claim → File → Symbol / Behavior → Exact SHA → Test → CI / Runtime Evidence
```

and challenges unsupported conclusions.

### Step 3 — PO / Management Gate
Management classifies:

- proven gaps
- OPEN semantics
- blockers
- minimum authorized action

### Step 4 — Minimal Implementation
Only authorized deltas are implemented:

```
KEEP → COMPLETE → CHANGE → BUILD
```

### Step 5 — Verification
Authorized changes require exact commit, targeted/regression tests, CI, runtime evidence where applicable, and independent verification.

### Step 6 — Controlled Pilot
Verified capability is exercised in actual HBI operation. Operational Reality is established by real traceable use.

## 19. Explicitly Not Authorized

Until the current gates close:

- new Recommendation architecture
- new scoring engine
- new Customer Fit engine
- new Relation engine/state
- new Need Mapping implementation
- new Problem Bank implementation
- schema/API changes
- questionnaire redesign
- synthetic customer-language corpus
- broad refactoring
- merge based only on an agent report

## 20. Classification Rule for Future Information

Every new report, proposal, issue, PR, or agent statement affecting this path must be classified as:

1. Historical / Governance Record
2. Current Master Repository Reality
3. Accepted Business Semantics
4. Open Business Question
5. Proven Gap
6. Implementation Proposal

No new document may silently redefine the path.

If a new claim conflicts with this baseline:

1. inspect Current Master
2. establish evidence
3. trace accepted semantics
4. calculate Delta
5. correct this baseline if necessary

The baseline never overrides evidence.

## 21. Final Management Map

```
CURRENT MASTER REALITY
→ EVIDENCE
→ ACCEPTED BUSINESS SEMANTICS
→ DELTA
→ BLOCKER?
→ MINIMUM ACTION
→ AUTHORIZATION
→ IMPLEMENTATION
→ VERIFICATION
→ CONTROLLED PILOT
→ OPERATIONAL REALITY
```

The objective is to finish HBI, not to create more documents, engines, abstractions, or parallel workstreams.

## 22. Current Stop Point

**Mission:** WP-0 — Recommendation Reality Map  
**State:** IN PROGRESS

Next sequence:

```
GPT-2
→ corrected WP-0 Reality Map from Current Master

GPT-1
→ independent verification

PO / Management
→ gate and authorization

Authorized implementation
→ only after the gate
```

Until then:

**Implementation remains NOT AUTHORIZED.**

## 23. Baseline Integrity Rule

This document is a **management baseline / WP-0 reference**.

It is not the technical source of truth.

If exact Current Master inspection contradicts a statement here:

> **Current Master Reality + Evidence wins.**

The document must then be corrected.

If accepted business semantics change through an explicit PO decision, the Delta must be recorded rather than silently rewriting history.

**Reality first. Evidence second. Accepted semantics third. Decision before authorization. Implementation last.**
