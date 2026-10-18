# HBI Phase 2 — Customer Language Discovery Criteria V1

## Status

- Phase 1 — Domain Skeleton V0.1: **ACCEPTED**
- Gate 1: **CLOSED**
- Phase 2 — Customer Language Discovery Criteria: **APPROVED**
- Phase 2 Customer Language Collection: **NOT STARTED**
- Phase 2 Customer Language Discovery Artifact / Corpus V0.1: **NOT YET PRODUCED**

This document records the approved operating contract for Phase 2. It is a discovery contract, not an implementation specification.

## Mission

Discover and register how customers actually express skin-related experiences, concerns, observations, and changes that may be relevant to HBI.

The output is a **Customer Language Discovery Artifact**, not a Problem Bank, Need Bank, Recommendation Logic, Diagnosis Taxonomy, or Product Mapping.

## Frozen Boundaries

The following remain prohibited in Phase 2:

- Problem Bank
- Need Bank
- Recommendation Logic
- Product Mapping
- Recommendation Scoring
- Diagnosis Taxonomy
- Treatment Logic
- Medical Decision Logic
- Schema
- Database Design
- API
- Implementation

### Core separation

Customer Language Discovery != Problem Discovery != Need Discovery != Diagnosis

A customer expression must not be silently transformed into a problem, need, diagnosis, product fit, or clinical mechanism.

## Source Separation

These source types must remain distinguishable:

1. Customer Expression
2. Operator Interpretation
3. Physician Observation
4. Scientific / Clinical Interpretation

Only Customer Expression is directly Customer Language.

Operator, physician, scientific, and other sources may be used for cross-checking, gap discovery, red-team review, and terminology validation, but must not be relabeled as Customer Expression.

### Provenance

Every registered expression must preserve, where available:

- Source Type
- Source Reference / Provenance
- Direct vs Reported

Allowed provenance categories include:

- Direct Customer Expression
- Reported Customer Expression
- Operator Paraphrase
- Physician Observation
- Other Source

## Customer Expression Rule

Preserve customer-level language as much as possible.

Allowed examples:

- "پوستم می‌سوزه."
- "هر چیزی می‌زنم اذیتم می‌کنه."
- "بعد از این کرم صورتم قرمز شد."

Forbidden transformations:

- "Barrier dysfunction دارد."
- "Inflammatory reaction دارد."
- "احتمالاً فلان بیماری را دارد."

Specialist terminology may be recorded as a separate interpretation or validation layer when justified by the source. It must not replace the original customer wording.

## Context Rule

Context may be recorded when it is actually reported or observed, for example:

- after product use
- after washing
- recent
- recurring
- seasonal

Context must not be converted into an interpretation such as:

- likely irritant reaction
- likely barrier damage
- probable diagnosis

## Ambiguity and Unknowns

Ambiguity is a valid result.

If an expression cannot be responsibly interpreted within the discovery evidence, mark it as **AMBIGUOUS** rather than forcing classification.

Unknowns must remain explicit.

Do not fill missing evidence with assumptions.

Generic "Confidence" is not a required Phase 2 field because it is ambiguous without a defined dimension. If confidence is later introduced, its dimensions must be explicit.

## Domain Challenge

The Domain Skeleton V0.1 is a **Draft / Breakable Discovery Scaffold**, not a final taxonomy.

Customer Language Discovery must be allowed to:

- Confirm a domain
- Challenge a domain
- Split a domain
- Merge domains
- Rename a domain
- Demote a domain
- Expose a domain as insufficient

Phase 2 is therefore not required to preserve the current D1–D10 structure.

Expressions that do not fit a current domain must remain visible as gaps or unabsorbed observations. They must not be forced into an existing domain merely to make the landscape look complete.

## Coverage

Coverage is not the number of collected expressions.

Phase 2 review must consider at least:

- Language Coverage
- Expression Diversity
- Source Diversity
- Domain Coverage
- Unknown Preservation
- Ambiguity Preservation
- Premature-Interpretation Avoidance

No fixed expression count or domain quota is imposed.

## Gap Handling

Use explicit states where appropriate:

- Known Gap
- Unknown
- Needs Further Discovery

Do not invent missing customer language.

Non-critical gaps may remain open during discovery, but they must be recorded and must block any later claim of completeness where relevant.

## Red-Team Checks

Before Phase 2 can be considered complete, review at minimum:

1. Did any Customer Expression secretly become a Problem?
2. Did specialist language replace customer language?
3. Was an observation or interpretation registered as Customer Language?
4. Did context become interpretation?
5. Was an ambiguous expression force-classified?
6. Did one dominant source create false coverage?
7. Did product-market language bias the discovery?
8. Did Customer Language actually challenge the Domain Skeleton where warranted?
9. Were Unknowns and Gaps preserved?
10. Are there expressions that no current domain can responsibly absorb?

## Gate 2 Entry

Gate 2 may begin because:

- Gate 1 is closed.
- Phase 2 criteria are approved.
- No Customer Language Collection has yet been treated as authoritative.

## Gate 2 Exit

Phase 2 may not be declared complete until:

- Customer Language Coverage is reviewed.
- Source Provenance is preserved.
- Ambiguity is preserved.
- Unknowns are preserved.
- Domain Challenge has been performed.
- Gaps are registered.
- Premature interpretation has been audited.
- Critical red-team failures are closed.

## Current Execution State

As of this record:

**PHASE 2 — CRITERIA APPROVED / COLLECTION NOT STARTED**

The next substantive artifact is:

**Customer Language Discovery Corpus V0.1**

It must be built from traceable source material and must not be fabricated from assumed customer behavior.

## Architectural Boundary

> Concept Boundary describes conceptual separation only. It does not define automatic transformation, mandatory workflow sequence, or implementation architecture.

Discovery remains separate from Validation.

Discovery asks what appears in the real-world space.

Validation asks how concepts, terminology, relationships, and clinical boundaries should subsequently be assessed.
