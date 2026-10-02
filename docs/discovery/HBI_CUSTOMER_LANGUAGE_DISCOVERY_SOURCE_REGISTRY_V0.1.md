# HBI Customer Language Discovery Source Registry V0.1

## Status

- Phase 2: ACTIVE
- Phase 2.0 — Source Set Establishment: IN PROGRESS
- Customer Language Corpus V0.1: BLOCKED pending source verification
- No source is treated as available merely because it is listed here.

## Purpose

This registry records the candidate source classes that may legitimately support Customer Language Discovery.

It does **not** claim that the underlying material exists, is accessible, or contains customer language. Availability must be verified before extraction.

## Source Registry

| Source ID | Source Type | Availability | Provenance Rule | Reliability Boundary | Allowed Use |
|---|---|---|---|---|---|
| S1 | Direct customer interviews / recorded customer statements | UNKNOWN | Preserve original wording and traceable source reference | Only the actual customer statement may be registered as Customer Expression | Discovery |
| S2 | HBI consultation / gallery records containing customer statements | UNKNOWN | Preserve record ID and distinguish direct customer wording from operator paraphrase | Existing records may contain interpretation; provenance must be separated | Discovery / Cross-check |
| S3 | Customer forms, messages, tickets, or other direct communications | UNKNOWN | Preserve source reference and direct/reported status | Only customer-originated wording qualifies as Customer Expression | Discovery |
| S4 | Operator reports / operator experience | UNKNOWN | Identify operator as source; never relabel operator interpretation as Customer Expression | Useful for gap/contradiction discovery, not direct customer-language evidence unless explicitly quoting a customer | Cross-check / Gap only |
| S5 | Physician observations / clinical notes | UNKNOWN | Preserve physician source and observation context | Physician terminology is not Customer Language unless explicitly quoting/reporting customer wording | Cross-check / Gap / Clinical relevance |
| S6 | Existing HBI discovery artifacts or project documents | UNKNOWN | Preserve document path/issue/PR and exact source location | May contain mixed source types; source identity must be retained | Cross-check / Gap |
| S7 | External customer-language sources | UNKNOWN | Record URL/document/source identity and retrieval context | Discovery signal only; not medical proof and not assumed to represent HBI customers | Discovery signal / Cross-check |
| S8 | Product / market language | UNKNOWN | Record product/market source separately from customer source | Capability context only; must not generate or redefine customer problems | Capability context / Gap discovery |

## Availability Policy

`UNKNOWN` is intentional.

A candidate source becomes `AVAILABLE` only after evidence establishes:

1. The material actually exists.
2. The material is accessible to the project team.
3. Its provenance can be preserved.
4. Its permitted use is compatible with the Phase 2 criteria.
5. Any privacy/confidentiality boundary required for use is understood.

Until then, it must not contribute expressions to the Corpus.

## Customer Expression Qualification

A source item qualifies for the Customer Language Corpus only when:

- the wording originates from a customer, or is explicitly reported as customer wording;
- provenance can be preserved;
- the wording is not silently rewritten into specialist terminology;
- direct vs reported status is recorded.

Operator, physician, scientific, and product-market statements remain separate source classes.

## Synthetic Content Rule

Synthetic examples may be used in methodology documentation or testing, but they are **not Customer Language Corpus entries** and must never be presented as observed customer language.

## Current Repository Evidence

A repository search was performed for customer-language/discovery material and customer-related artifacts. No existing repository result was found that is sufficient, by itself, to establish an available Customer Language source set.

Therefore the registry records candidate source classes as `UNKNOWN` rather than inventing availability.

## Phase 2.0 Exit Criteria

Phase 2.0 can close only after each candidate source relevant to execution is classified as:

- AVAILABLE
- UNAVAILABLE
- NOT AUTHORIZED
- NOT RELEVANT
- UNKNOWN WITH EXPLICIT BLOCKER

and the evidence/provenance for AVAILABLE sources is recorded.

## Next Action

Do not generate Customer Language Corpus entries yet.

First verify the availability and provenance of the candidate source classes above. Only verified source material may enter Corpus V0.1.

## Boundary

Customer Language Discovery remains distinct from Problem Discovery, Need Discovery, Diagnosis, Recommendation, Product Mapping, and Implementation.
