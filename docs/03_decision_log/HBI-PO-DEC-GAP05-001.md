# HBI-PO-DEC-GAP05-001 — GAP-05 L1 Semantic Need Contract

**Status:** PO DECISION RECORDED — CONTRACT DEFINITION COMPLETE — IMPLEMENTATION AUTHORIZED AND REALIZED  
**Date:** 2026-09-16  
**Mission:** A2A-COM-004  
**Related:** F4 / GAP-05 — Semantic Need Derivation & Requirement Quality
**Runtime baseline:** `master @ 7d273e84856086a61d2c9d272fa170c2d7dbca99`

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

If the input cannot be resolved deterministically, the system must preserve the unresolved/unknown state rather than inventing meaning. The implemented runtime applies this boundary through GAP-05 L1 normalization and its acceptance tests.

## 5. Acceptance criteria for implementation

The implementation of this contract is acceptable only if it demonstrates, with tests/evidence:

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

These criteria are realized by the current master implementation and its focused regression/acceptance evidence.

## 6. Explicitly deferred

The following are **not selected or authorized** by this decision:

- embeddings or vector similarity;
- LLM-based Need inference;
- ontology/knowledge-graph construction;
- new Problem or Assessment entities/tables;
- scoring or weighting changes;
- reopening GAP-01, GAP-03, or GAP-04;
- changing Issue #37 status;
- broad refactoring outside the GAP-05 contract.

GAP-05 L1 implementation itself is no longer deferred: it was explicitly authorized by the PO and is present on the current master baseline.

## 7. Current Reality vs target contract

The current runtime on master realizes the GAP-05 L1 boundary: Decision State factors are normalized into bounded canonical Needs; Product matching uses the explicitly approved ProductKnowledge `known_use_cases` semantic surface; Product-side vocabulary is independent from Customer vocabulary; unmapped/ambiguous input is not silently guessed; and the existing scoring/weighting formula remains unchanged.

Therefore, for GAP-05:

`CURRENT RUNTIME = IMPLEMENTED L1 CONTRACT`

Implementation status is established by the merged runtime and its acceptance evidence, not by this decision record alone.

## 8. Authorization boundary

The PO separately authorized GAP-05 L1 implementation after the contract decision. That authorization has been executed and verified on the current master baseline `7d273e84856086a61d2c9d272fa170c2d7dbca99`.

This record therefore no longer states that GAP-05 implementation is unauthorized or deferred.
