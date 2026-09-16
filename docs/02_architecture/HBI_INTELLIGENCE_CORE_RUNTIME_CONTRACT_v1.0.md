# HBI Intelligence Core Runtime Contract v1.0

**Mission:** HBI — MISSION A | INTELLIGENCE CORE 0→100  
**Baseline:** `fc27967d3c759c32a1e5c5136dbfdf0aa53e7c08`  
**Status:** MISSION-A IMPLEMENTATION BASELINE  
**Scope:** Intelligence Core runtime boundary and consumption contract

## 1. Purpose

This document makes the current Intelligence Core boundary explicit so Product/Business Integration can consume the runtime without inventing missing semantics.

The core decision path is:

`Customer Profile → Case Scope → Decision State → Factor → Canonical Need → Product Knowledge / Evidence → Eligibility Gates → Ranking → Recommendation Result`

`Problem` and `Assessment` are not mandatory persisted MVP entities. A computed Decision State is the current decision representation unless a separately authorized persistence decision changes that boundary.

## 2. Domain boundary

| Concept | Current MVP role | Persistence | Contract status |
|---|---|---|---|
| Customer | Business/customer identity and profile owner | Persisted | Active |
| Case | Decision context and ownership boundary | Persisted | Active |
| Concern | Raw customer-declared input | Within profile / Decision State input | Input, not Need |
| Factor | Computed/declared decision input with source and validity | Decision State representation | Active MVP representation |
| Problem | Interpreted problem context | Not independently persisted | Deferred architecture |
| Assessment | Structured evaluation concept | Not independently persisted | Deferred architecture |
| Need | Canonical decision requirement | Decision State + Recommendation trace | Active |
| Evidence | Product claim/evidence with provenance and QA/conflict state | Persisted | Active |
| Decision State | Computed snapshot of the current decision inputs/state | Not independently persisted | Active MVP representation |
| Decision | Persisted standalone decision entity | Not verified/required | Deferred architecture |
| Recommendation | Product-specific decision result | Persisted | Active |
| Feedback | Outcome signal from recommendation usage | Full business flow deferred | Contract boundary only |

## 3. Required semantics

### 3.1 Concern → Factor → Need

- Raw Concern is never treated as a canonical Need merely because the strings resemble one another.
- Current runtime creates declared Factors from customer concerns.
- GAP-05 L1 normalization converts only approved mappings into canonical Needs.
- Unmapped or ambiguous input remains explicit and cannot be silently guessed into a Need.
- Canonical Need mappings retain the originating factor value, source, validity, and mapping rule.

### 3.2 Evidence

Evidence supplied to reasoning retains provenance fields including evidence identity, claim identity/type, source reference/type, evidence strength, QA status, and conflict status.

Only evidence explicitly approved for decision use contributes to the current Evidence Score. Conflict and Unknown are surfaced rather than silently converted into certainty.

### 3.3 Reasoning

`ReasoningEngine.run()` is a computed-only operation. It does not persist a ReasoningResult. Its result may contain evidence references, conflicts, unknowns, claim-boundary violations, warnings, rationale, engine version, and scoring outputs when the scoring inputs are supplied.

### 3.4 Eligibility before ranking

The decision sequence is:

1. obtain verified active products;
2. eliminate unavailable inventory before candidate recommendation;
3. compute Need match and Evidence score;
4. run reasoning and existing hard-gate logic;
5. map eligibility;
6. persist only eligible recommendation results into the returned recommendation set;
7. rank retained eligible candidates.

Ranking cannot restore a candidate rejected by a hard gate.

The current scoring formula, weights, thresholds, and Issue #37 remain frozen and are outside this Mission's authorization.

## 4. Recommendation consumption contract

A Product/Business Integration consumer may rely on these Recommendation fields:

| Field | Meaning |
|---|---|
| `case_id` | originating Case |
| `product_id` | selected product |
| `need_match_score` | frozen Need-match signal |
| `evidence_score` | approved-evidence signal |
| `eligibility_status` | final product eligibility state |
| `ranking_score` | score of a retained candidate |
| `ranking_reasons` | runtime rationale / explanation text |
| `exclusion_reasons` | reason a candidate was excluded when represented by the persistence surface |
| `evidence_refs` | serialized provenance references used by reasoning |
| `warnings` | explicit uncertainty, gate, or trace warnings |

The DTO additionally exposes `final_score`, `confidence`, `eligibility`, `reasoning`, `availability`, and `price` as the current integration surface.

Consumers MUST NOT infer a Problem entity, a persisted Decision entity, a new scoring policy, or a missing Evidence fact from the absence of a field.

## 5. Explainability contract

For an eligible recommendation, the explanation must be derived from actual runtime decision inputs. At minimum, the persisted result exposes:

- Need-match signal;
- Evidence score;
- eligibility state;
- ranking/reasoning text;
- evidence references;
- warnings where uncertainty or gates were relevant.

An explanation must not introduce product facts that are absent from ProductKnowledge, Evidence, Inventory, or other verified runtime inputs.

## 6. Unknown / Conflict / insufficient information

The core distinguishes:

- **UNKNOWN:** information is unavailable or explicitly unknown;
- **CONFLICT:** available evidence contains conflicting claims;
- **AMBIGUOUS NEED:** input partially maps to known concepts but has no approved exact mapping;
- **UNMAPPED NEED:** no approved mapping exists;
- **INSUFFICIENT:** no usable canonical Need remains;
- **REFERRAL:** active medical context requires professional review under the existing hard gate;
- **INELIGIBLE_PENDING_REVIEW:** candidate cannot be recommended without review/resolution.

None of these states may be represented to the consumer as a positive fact that the system did not actually establish.

## 7. Specialist override boundary

The current Intelligence Core exposes the existing Case/operator override state for inspection, but this contract does not authorize an untraceable override mechanism. A future override implementation must preserve the original evidence/decision inputs and record what was overridden, by whom/what role, and why.

## 8. Feedback boundary

Mission A exposes the architectural boundary:

`Recommendation Result → Feedback Contract`

Full customer/specialist outcome capture, learning eligibility, promotion, rollback, and business workflow belong to Mission B. Feedback must not silently rewrite production rules, Need mappings, scoring, or ProductKnowledge.

## 9. Explicit non-authorizations

This runtime contract does not authorize:

- a new Problem/Assessment entity or migration;
- a new FactorDefinition/CaseFactor persistence model;
- Decision State persistence;
- scoring/weight/threshold changes;
- Issue #37 changes;
- Medical Hard Gate policy changes;
- LLM/embedding/ontology inference;
- gallery UI or business workflow implementation.

## 10. Verification requirement

A claim of conformance requires direct repository evidence and relevant automated tests. A documented contract is not evidence that runtime behavior exists.

`DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED`

**END OF CONTRACT**
