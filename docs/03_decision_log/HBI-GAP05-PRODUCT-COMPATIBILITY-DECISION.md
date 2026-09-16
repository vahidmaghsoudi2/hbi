# GAP-05 Product Matching — PO Decision Record

**Decision status:** PO DECISION RECORDED — IMPLEMENTATION AUTHORIZED
**Date:** 2026-09-16

## Decision

The PO approves `ProductKnowledge.known_use_cases` as the official, controlled semantic surface for Product ↔ Need compatibility in the GAP-05 L1 MVP.

## Implementation boundary

- Customer Needs are first normalized to canonical Need ids by the existing GAP-05 L1 deterministic normalization.
- `ProductKnowledge.known_use_cases` is normalized through an explicit product-side vocabulary to the same canonical Need ids.
- Product matching is canonical-to-canonical; raw token overlap is not the compatibility rule.
- Existing frozen scoring math and thresholds remain unchanged. Only the semantic input surface to `need_match` changes.
- Unknown/unmapped product use-case phrases are not guessed into canonical compatibility.
- Existing MVP seed category phrases are handled only through explicit, auditable product-side mappings.
- No new Product/Need entity or scoring policy is introduced by this decision.

## Acceptance intent

The runtime must be able to demonstrate:

`Decision State → Canonical Need → controlled ProductKnowledge known_use_cases → canonical compatibility → unchanged need_match scoring → existing ReasoningEngine / Eligibility / Recommendation path`

## Non-goals

- No embeddings, vector similarity, ontology, graph, or LLM inference.
- No scoring/weight/threshold changes.
- No reopening closed GAPs.
- No Problem/Assessment entity.
