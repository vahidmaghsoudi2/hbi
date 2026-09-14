# HBI-PO-DEC-GAP05-001 — GAP-05 L1 Semantic Need Contract

**Status:** PO DECISION RECORDED — CONTRACT DEFINITION COMPLETE — IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-09-14  
**Mission:** A2A-COM-004  
**Related:** F4 / GAP-05 — Semantic Need Derivation & Requirement Quality

## 1. Decision

The MVP adopts **L1 — Controlled Semantic Normalization**.

A Need must not remain merely a raw lexical copy of customer wording as its intended semantic contract. The MVP may transform the Decision State into a bounded, deterministic, auditable canonical Need using an approved canonical vocabulary, approved synonym/phrase mappings, and explicit normalization rules.

This decision does not select embeddings, ontology, LLM-based semantic inference, or any other implementation technology.

## 2. Domain boundaries

### Concern
Raw customer-declared wording. Concern is input, not itself a product requirement.

### Factor
A computed Decision State item carrying interpreted input with provenance/validity. A Factor is not automatically a Need.

### Need
A normalized representation of the customer's relevant requirement, derived **only from Decision State**, with sufficient bounded meaning to support an MVP product decision.

### Product Matching
Matching must operate on the normalized/canonical Need representation against an explicitly compatible ProductKnowledge semantic surface. L1 requires deterministic canonical equivalence rather than relying on raw surface-form coincidence as the intended contract.

## 3. Normative rules

1. `Concern → Factor → Need` remains the controlled derivation boundary.
2. Raw `customer_profile.concerns` must not bypass Decision State to become Need.
3. Normalization must be deterministic and auditable.
4. An approved synonym/phrase may resolve to the same canonical Need.
5. Unmapped, ambiguous, or insufficient input must not be silently guessed into a canonical Need.
6. Need must remain traceable to its originating Factor and declared source/validity.
7. Product matching consumes the canonical Need representation.
8. Evidence supports product suitability, claims, conflicts, unknowns, and evidence scoring; it does not silently rewrite Need extraction.
9. Unknown and Conflict states must not be silently normalized into certainty.
10. Medical Context remains contextual/non-diagnostic and does not authorize diagnostic inference.
11. The existing scoring/weighting formula remains frozen. L1 changes the semantic input contract, not scoring mathematics.
12. No recommendation may be justified solely by a guessed or untraceable Need.

## 4. Minimum-meaning rule

For MVP design, a Need has sufficient minimum meaning only when it resolves to an approved canonical concept through an explicit normalization rule or mapping.

If the input cannot be resolved deterministically, the system must preserve the unresolved/unknown state rather than inventing meaning. Exact gating behavior for insufficient Need meaning is a design/implementation acceptance criterion and is not claimed as current runtime behavior by this record.

## 5. Acceptance criteria for implementation

An implementation of this contract is acceptable only if it demonstrates, with tests/evidence:

- equivalent approved terms resolve to the same canonical Need;
- approved synonym/phrase mappings are deterministic;
- unrelated terms do not collapse into the same Need without an explicit rule;
- unmapped/ambiguous input is not silently guessed;
- normalization is auditable and traceable to Factor/source;
- canonical Need is the representation used for Product matching;
- ProductKnowledge compatibility is explicit and inspectable;
- Evidence remains separate from Need derivation unless a future decision changes that boundary;
- Unknown/Conflict constraints remain effective;
- scoring weights/formula are unchanged;
- no new Problem/Assessment entity is introduced as an implicit consequence of GAP-05.

## 6. Explicitly deferred

The following are **not selected or authorized** by this decision:

- embeddings or vector similarity;
- LLM-based Need inference;
- ontology/knowledge-graph construction;
- new Problem or Assessment entities/tables;
- scoring or weighting changes;
- reopening GAP-01, GAP-03, or GAP-04;
- changing Issue #37 status;
- broad refactoring outside the GAP-05 contract;
- implementation itself.

## 7. Current Reality vs target contract

Current runtime reality remains the F4 finding: customer concerns are converted into Decision State factors, Needs are currently derived largely by copying factor values, and current product matching uses token-overlap heuristics. The L1 decision defines the target MVP contract; it does **not** claim that the target behavior already exists.

Therefore:

`CURRENT REALITY ≠ L1 CONTRACT ≠ IMPLEMENTATION AUTHORIZATION`

## 8. Authorization boundary

This record permanently records the PO's L1 decision and the contract definition. **Implementation is NOT AUTHORIZED by this record.** A separate explicit PO authorization is required before code/PR work begins.
