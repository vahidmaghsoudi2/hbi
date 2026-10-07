# HBI — CONSOLIDATED REALITY & EXECUTION PATH BASELINE

## Purpose

This document is the single consolidated management map for the current HBI execution path. It prevents drift between historical proposals, repository capability, business semantics, agent reports, and operational reality.

It is a **reality and execution map**, not an implementation specification.

## Current Governance State

- Repository: `vahidmaghsoudi2/hbi`
- Management baseline: `a05e1708d24e2485c5f6307f8f85b2c676b6017d`
- WP-0 — Recommendation Reality Map: **IN PROGRESS**
- GPT-2 Reality Audit: **IN PROGRESS / classification correction required**
- GPT-1 Independent Verification: **WAITING for corrected WP-0**
- Implementation: **NOT AUTHORIZED**
- Architecture / Schema / API / Recommendation / Scoring changes: **NOT AUTHORIZED**
- Merge: **NOT AUTHORIZED unless separately authorized by PO**

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

The correct comparison is:

```
Current Repository Reality + Accepted Business Semantics = Delta
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

Current state:

- Skin Problem Space Map V0.1: **ACCEPTED / FROZEN**
- Problem Bank V1: **ACCEPTED WITH CONDITIONS**
- Problem Bank implementation: **NOT AUTHORIZED**

Known open items include P08 canonical-status strength, HBI Relevance admission criterion, and S01/S02 direct artifact inspection. These were not blockers for pre-pilot readiness.

Problem Bank V1 is sufficient for the next controlled stage, but is not claimed to be field-validated or complete.

## 2. Problem → Need Contract

Current baseline:

```
docs/contracts/problem-need/PROBLEM_NEED_CONTRACT_V0.1.1.md
```

- Commit: `5ea25188d3cffbe3ebf286e80cae7de30643c475`
- Blob: `b0db2d0fd0ef03d499caaeb131c63c16c4ce8e83`
- Base: `a05e1708d24e2485c5f6307f8f85b2c676b6017d`
- Status: **BASELINED — ACCEPTED WITH CONDITIONS**

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

## 3. Customer / Consultation

The repository has an established Customer / Case / Consultation Context path and recommendation-related capabilities.

Verified milestones:

- Consultation vertical slice: PR #215, accepted at `032e14ad031007616dfea6c678a559bf2f48c040`
- Bounded Skin Next Question: PR #226, accepted at `a8f7c941496eb4ee5d1f5e64be2233763f1f2377`
- Customer Profile V1.1: PR #190, approved at `8bd7af6e9cf121f4569ebb0ba6782d61c2f00390`

The five Customer Profile boxes are a UI projection, not a five-entity data model.

No recommendation/scoring/evidence-gate change follows from Customer Profile V1.1.

## 4. Customer Reality

HBI has not yet started normal operational customer use.

Therefore:

- Customer Reality is not claimed as verified.
- Customer Language is not claimed as verified.
- Synthetic examples cannot become customer evidence.
- Repeated repository searches must not be used to manufacture nonexistent customer history.

The future gate is controlled acquisition of traceable real customer-originated evidence.

Customer Reality must remain separate from repository capability.

## 5. Product / Product Knowledge

The Product/Product Knowledge path contains substantial capability for:

- Product identity and lifecycle
- Product intake
- Product knowledge
- Evidence
- QA
- Compatibility/reasoning
- Inventory-related eligibility

Broad lifecycle:

```
Introduce → Duplicate → Research Draft → Enrich → Evidence / QA
→ PO Review → Approve → Activate → Inventory → Recommendation
```

Real Product Pilot remains an open operational area.

## 6. Recommendation — Current Connected Path

Current path to audit:

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

This is a map of connected repository capabilities, not a claim that every business semantic is complete.

## 7. WP-0 Recommendation Reality Map

Mandatory stages:

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

For every stage, WP-0 must separately determine:

1. Repository Capability
2. Operational Reality
3. Evidence
4. Status
5. Accepted Business Meaning
6. Delta
7. Blocking?
8. Minimum Next Action

Required table:

| Stage | Repository Capability | Operational Reality | Evidence | Status | Delta | Blocking? | Minimum Next Action |
|---|---|---|---|---|---|---|---|
| Customer Input | verify | verify separately | exact | status | delta | yes/no | minimum |
| Canonical Need | verify | verify separately | exact | status | delta | yes/no | minimum |
| Candidate Universe | verify | verify separately | exact | status | delta | yes/no | minimum |
| Relation | verify | verify separately | exact | status | delta | yes/no | minimum |
| Eligibility | verify | verify separately | exact | status | delta | yes/no | minimum |
| Customer Fit | verify | verify separately | exact | status | delta | yes/no | minimum |
| Scoring | verify | verify separately | exact | status | delta | yes/no | minimum |
| Ranking | verify | verify separately | exact | status | delta | yes/no | minimum |
| Explanation / Evidence | verify | verify separately | exact | status | delta | yes/no | minimum |
| Operator Decision | verify | verify separately | exact | status | delta | yes/no | minimum |

WP-0 identifies reality and deltas; it does not redesign architecture.

## 8. Candidate Universe

Candidate Universe must be examined **before** Relation and Eligibility.

Key question:

> Which products enter the candidate set, and why?

Candidate formation, Relation, Eligibility, and Ranking must remain separate concepts.

Current repository reports indicate hard candidate/eligibility gates involving:

```
Identity Verified + Active + QA Valid + Inventory > 0
```

This is repository behavior to be verified against exact code and accepted semantics. It must not silently become a business contract.

## 9. Relation / Compatibility

Repository capability includes ProductKnowledge-driven compatibility/use-case matching into canonical Need IDs and a need-match signal.

Current classification:

- Compatibility mechanism: **repository capability reported/proven subject to exact evidence check**
- Independent Relation state such as `RELATED / NOT_RELATED / UNKNOWN`: **not established as an independent repository component**
- Whether such an independent state is required by accepted V1 semantics: **OPEN until authoritative evidence is traced**

Missing a component does not authorize building it.

## 10. Eligibility

Eligibility exists in current Recommendation behavior.

Reported gates:

```
Identity Verified + Active + QA Valid + Inventory > 0
```

Exact implementation and accepted semantics remain part of WP-0 verification.

Boundary:

```
Eligibility ≠ Ranking
```

## 11. Customer Fit

Customer / Case / Consultation Context and ProfileFact-related capabilities can provide customer context.

No independent standalone Customer Fit Engine has been established.

Classification:

- Customer context consumption: repository capability exists.
- Independent Fit Engine: not established.
- Requirement for a separate Fit Engine: **OPEN** unless required by an authoritative business artifact.

No Fit Engine should be built merely because the code does not use that name.

## 12. Scoring

Existing scoring behavior:

- Need: **0.50**
- Evidence: **0.30**
- Inventory: **0.20**

Scoring is not authorized for redesign.

## 13. Ranking

Ranking orders eligible candidates by ranking score.

```
Ranking orders.
Eligibility excludes.
```

Intended result behavior:

- backend result set remains complete for eligible results
- UI may initially show up to five
- Show More exposes additional results
- operator remains final decision-maker

## 14. Explanation / Evidence / Trust Trace

Recommendation explanation and trace capabilities exist, including evidence references and Trust Trace.

A current limitation reported in audit is that products excluded before a Recommendation record exists do not necessarily receive a full persisted why-not trace.

This is a repository limitation.

Whether full exclusion observability is a V1 business requirement remains **OPEN** unless tied to an authoritative acceptance criterion.

## 15. Operator Decision

Governing boundary:

```
Recommendation ≠ Decision
```

The system provides reasoned suggestions; the operator can inspect reasons, evidence, warnings and update needs and makes the final selection/decision.

Existing specialist/operator override behavior includes ACCEPT / REJECT / MODIFY_SELECTION.

## 16. End-to-End Direction

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

Not every arrow is currently proven as a complete business implementation. WP-0 determines the exact status of each.

## 17. Five Controlled Questions — Not Five Proven Gaps

1. **Candidate Universe:** What exactly constitutes the candidate set, and is current formation aligned with accepted semantics?
2. **Relation:** Is current compatibility/use-case matching sufficient, or is an explicit Relation boundary required?
3. **Customer Fit:** What exactly does Customer Fit mean, and is current customer-context consumption sufficient?
4. **Exclusion Observability:** Which exclusions must be explainable/auditable, and to what level?
5. **Operational Reality:** Which capabilities have actually been exercised in real HBI operation?

No question becomes a build requirement without an evidence-backed business/contract decision.

## 18. Execution Route

### Step 1 — Close WP-0
GPT-2 completes the corrected Recommendation Reality Map.

### Step 2 — Independent Verification
GPT-1 independently checks Claim → File → Symbol/Behavior → Exact SHA → Test → CI/Runtime evidence and challenges unsupported conclusions.

### Step 3 — PO / Management Gate
Management classifies real gaps, OPEN semantics, and blockers and authorizes only the minimum necessary action.

### Step 4 — Minimal Implementation
Only authorized deltas are implemented:

```
KEEP → COMPLETE → CHANGE → BUILD
```

### Step 5 — Verification
Authorized changes require exact commit, targeted/regression tests, CI, runtime evidence where applicable, and independent verification.

### Step 6 — Controlled Pilot
Verified capability is exercised in actual HBI operation; operational reality is established by real traceable use.

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
2. Repository Reality
3. Accepted Business Semantics
4. Open Business Question
5. Proven Gap
6. Implementation Proposal

No new document may silently redefine the path.

Conflicts must identify the exact evidence, artifact, SHA, semantic reason, and whether the conflict is historical, repository-level, or business-level.

## 21. Final Management Map

```
CURRENT REALITY
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
**Next sequence:**

```
GPT-2 → corrected WP-0 Reality Map
GPT-1 → independent verification
PO / Management → gate and authorization
Authorized implementation → only after gate
```

Until then:

**Implementation remains NOT AUTHORIZED.**

## 23. Baseline Integrity

This document is a management baseline, not a substitute for repository evidence.

If exact repository inspection contradicts a statement here, repository evidence wins and this baseline must be corrected.

If accepted business semantics change through an explicit PO decision, the Delta must be recorded rather than silently rewriting history.

**Reality first. Contract second. Verification before authorization. Implementation last.**
