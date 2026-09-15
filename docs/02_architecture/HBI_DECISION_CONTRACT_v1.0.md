# HBI Decision Contract v1.0

**Mission:** HBI-ARCH-001 — Decision Architecture & Contract Baseline  
**Baseline:** `master @ 87d83e4e6ba4f6c85e19d6a1fb595ce7a360bf6d`  
**Status:** PO ACCEPTED — CONTRACT DRAFT FOR REVIEW  
**Scope:** Architecture / Decision / Governance only

## 1. Purpose

This document converts the six PO-accepted architecture decisions of HBI-ARCH-001 into a bounded Decision Contract.

The contract defines what HBI must know before recommending a product, what can eliminate a candidate, what only affects ranking, what minimum meaning is required from a Need, which decision information should be durable, which domain concepts remain future architecture, and how feedback/learning is bounded.

This document does **not** authorize implementation by itself.

## 2. Governing principles

1. HBI is a Problem-Centered Decision Support System; this identity does not require a `Problem` table in the MVP.
2. `Concern != Problem != Factor != Need != Decision State`.
3. Need is derived only from Decision State and uses the GAP-05 L1 controlled semantic normalization contract.
4. Evidence, Unknown, and Conflict constrain decision confidence and suitability; they must not be silently converted into certainty.
5. Elimination/gating occurs before ranking.
6. Ranking must never rescue a candidate that failed a hard gate.
7. No recommendation is justified by invented, guessed, or untraceable information.
8. Current scoring/weighting remains frozen; this contract does not approve new weights.
9. Medical Context is contextual and non-diagnostic.

## 3. Decision object

For an MVP decision, HBI must be able to represent at least:

- the originating Case/customer scope;
- the current interpreted Factors and their provenance/validity;
- normalized canonical Needs and their normalization audit;
- unresolved/ambiguous Need information;
- relevant Evidence and its suitability/unknown/conflict implications;
- product availability/inventory state;
- product-level suitability/eligibility outcome;
- the reason a product was eliminated or retained;
- ranking signals for retained candidates;
- uncertainty/conflict and medical-context flags when applicable.

A Decision State may remain computed/in-memory in MVP. Persistence is addressed separately in Section 7.

## 4. Gate / Filter / Ranking / Signal contract

### 4.1 Gate

A **Gate** is a hard condition. If it fails, the product is not eligible for recommendation and ranking must not restore eligibility.

Examples of current hard-gate classes include:

- unavailable / out-of-stock candidate;
- critical unknown that blocks suitability;
- medical-context referral condition where recommendation is not permitted;
- insufficient usable Need meaning;
- product need match below the accepted minimum threshold;
- evidence/eligibility failure that the decision engine marks as non-eligible.

The exact thresholds and business policy must be explicit in the implementation contract before any change to them.

### 4.2 Filter

A **Filter** removes candidates from the decision set based on a defined business or technical constraint before ranking. A filter must have an explicit reason and must not be confused with a ranking penalty.

### 4.3 Ranking

**Ranking** orders candidates that have already passed all hard gates. Ranking cannot turn an ineligible candidate into an eligible recommendation.

The current scoring formula is treated as frozen runtime behavior until a separate PO decision changes it.

### 4.4 Signal

A **Signal** is information used to explain, compare, or prioritize an otherwise eligible candidate. A signal is not automatically a hard gate.

Every signal used in a decision must have a defined semantic role: gate, filter, ranking, or explanatory signal.

## 5. Minimum-Meaning Need contract

A Need has sufficient minimum meaning for MVP product decision only when it resolves to an approved canonical concept through an explicit deterministic normalization rule or approved mapping.

Therefore:

- approved synonym/phrase → canonical Need;
- exact registered canonical concept → canonical Need;
- ambiguous/partial/unmapped phrase → unresolved state;
- unresolved state must not be silently guessed into a Need;
- if no usable canonical Need remains, the decision is insufficient for recommendation.

Minimum meaning is semantic, not merely lexical: a matching string alone is insufficient unless the mapping is approved.

The existing GAP-05 L1 normalization implementation is the runtime realization of this boundary; this document defines the architectural contract.

## 6. Decision State persistence contract

### MVP position

Decision State may remain a computed snapshot during the current MVP phase. Persistence of the full Decision State is an architectural **OPEN IMPLEMENTATION DECISION**, not an immediate requirement to create a new table/entity.

### Required future property

If/when persistence is authorized, a persisted decision snapshot must make it possible to reconstruct:

- what the system knew at decision time;
- what it did not know;
- what was ambiguous or conflicting;
- which Needs were accepted;
- which gates eliminated candidates;
- which evidence/product facts supported the outcome;
- why the final recommendation was produced.

Persistence must preserve decision-time provenance and must not silently represent a later recomputation as the historical decision.

## 7. Problem / Assessment contract

### Problem

`Problem` is a future domain concept representing the customer's interpreted problem context. It is not equivalent to raw Concern and is not required as an independent MVP entity by this contract.

### Assessment

`Assessment` is a future domain concept representing structured evaluation of the Problem/Factors. It is not a diagnosis entity and is not required as an independent MVP entity by this contract.

### Boundary

No Problem/Assessment entity, table, API, migration, or mandatory runtime hop is authorized by this contract.

Future introduction requires a separate PO-approved design decision defining lifecycle, ownership, persistence, and traceability.

## 8. FactorDefinition / CaseFactor contract

The current MVP may represent Factors as computed Decision State items with provenance and validity.

A future `FactorDefinition` may define reusable factor semantics, while a future `CaseFactor` may represent a case-specific factor instance. These are architectural options, not current implementation requirements.

Any future adoption must define:

- factor identity and semantic definition;
- source/provenance;
- validity/status;
- relationship to Case and Decision State;
- relationship to Problem/Assessment if those concepts are later introduced;
- versioning/change behavior.

No new Factor entities are authorized by this contract.

## 9. Feedback / Learning contract

HBI should eventually learn from real-world outcomes, but learning must be evidence-bound and governed.

Future feedback must distinguish at least:

- recommendation shown;
- recommendation accepted/rejected;
- product purchased/used where observable;
- customer/specialist outcome feedback;
- outcome confidence and provenance;
- adverse/negative outcome where reported;
- whether feedback is suitable for model/rule learning.

Feedback must not automatically rewrite production decision rules, Need mappings, scoring, or ProductKnowledge. Any learning/update path requires explicit validation, provenance, versioning, rollback, and PO-approved promotion rules.

Therefore Feedback/Learning is a future architecture capability, not an automatic online-learning mechanism in the MVP.

## 10. Decision traceability

The minimum target trace is:

`Customer → Case → Factor/Decision State → Need → Product Knowledge/Evidence → Gate → Ranking → Recommendation`

Where a future Problem/Assessment runtime is introduced, the target trace may become:

`Customer → Case → Problem → Assessment/Factor → Decision State → Need → Product → Recommendation`

The future chain must not be retrofitted into MVP merely for structural completeness.

## 11. Acceptance criteria for future implementation

An implementation claiming conformance to this contract must demonstrate:

1. hard gates eliminate candidates before ranking;
2. ranking never rescues a failed gate;
3. every elimination has an auditable reason;
4. canonical Need is traceable to Factor/source;
5. ambiguous/unmapped Need is preserved rather than guessed;
6. insufficient Need blocks recommendation when minimum meaning is absent;
7. Evidence/Unknown/Conflict boundaries remain explicit;
8. current scoring/weights are unchanged unless separately authorized;
9. ProductKnowledge remains the declared product-matching semantic surface;
10. medical context remains contextual/non-diagnostic;
11. any persisted decision preserves decision-time provenance;
12. future Problem/Assessment/Factor entities are not introduced implicitly;
13. feedback cannot silently modify production behavior;
14. all policy/threshold/weight changes require explicit PO decision.

## 12. Explicit non-authorizations

This contract does not authorize:

- new Problem or Assessment entities/tables;
- new FactorDefinition/CaseFactor entities;
- Decision State persistence implementation;
- Feedback/Learning implementation;
- scoring or weighting changes;
- embeddings, LLM-based semantic inference, or ontology construction;
- reopening GAP-01, GAP-03, or GAP-04;
- changing Issue #37 status;
- direct push to `master`;
- implementation without a separate authorization where required by governance.

## 13. Decision Package status

**Architecture decisions:** ACCEPTED by PO for all six items.  
**Contract:** drafted here for repository review and independent verification.  
**Implementation authorization:** NOT GRANTED by this document.  
**Next governance step:** independent review by Grok-1, then PO/Team integration and explicit implementation authorization only where necessary.
