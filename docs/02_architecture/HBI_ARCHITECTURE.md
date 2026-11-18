# HBI Architecture

**Last Updated:** 2026-11-18  
**Architecture decision:** [HBI-PO-DEC-CKER-001 — Central Knowledge & Evidence Repository](../03_decision_log/HBI-PO-DEC-CKER-001.md)

## Backend Layers

| Layer | Path | Gate | Status |
|---|---|---|---|
| Models | app/models/ | 6-1 | Existing model layer; see current Gate evidence |
| Repositories | app/repositories/ | 6-2 | Existing repository layer; see current Gate evidence |
| Services | app/services/ | 6-3 | Existing service layer; see current Gate evidence |
| Interface (Facade/DTO/CLI) | app/interface/ | 6-4 | Existing interface layer; acceptance remains governed by its current Gate |

## Knowledge and Evidence architecture

HBI uses one logical **HBI Central Knowledge & Evidence Repository (CKER)** as the governing source-of-truth boundary for curated knowledge and its supporting Evidence.

- **Encyclopedia / curated Knowledge** is the human-facing, organized knowledge core of CKER.
- **Evidence** is the internal structured layer of atomic, source-bound claims. It is not a separate repository.
- Original manufacturer documents, physical package information, scientific publications, regulatory sources and other primary artifacts remain independently identifiable sources. CKER stores traceable claims and curated synthesis; it does not replace the original source.
- Each material claim retains its source, claim type, QA state, conflict state and applicable scope. Article-level editorial review does not replace claim-level Evidence QA.
- **ProductKnowledge** remains the product-scoped operational projection consumed by the recommendation runtime. It is not a parallel master knowledge repository and must follow its existing evaluated-Evidence rules.
- Product identity, product QA/lifecycle, Inventory, G8 and Recommendation eligibility remain separate authorities/gates.

Canonical governance flow:

Original source → atomic Evidence → curated CKER Knowledge / Encyclopedia → ProductKnowledge → eligibility gates → Recommendation

This is a logical architecture boundary across existing canonical storage surfaces. It does not imply a new ORM entity/table, database, schema migration, or separate GitHub repository.

## Decision Support Flow

Customer → Case → Decision State / Factors / Needs → ProductKnowledge + eligible Evidence → Reasoning → Eligibility Gates → Recommendation → Product / Inventory → Outcome

The exact runtime contract and hard gates remain defined by the active decision and domain contracts. Ranking cannot rescue a candidate that failed a hard gate.

## Architecture Constraints

- The currently locked schema remains locked; any schema change requires its own Change Request and explicit authorization.
- Facades are Use-Case-Oriented, not CRUD-Oriented.
- Interface code has no direct access to Repository, Model or Database layers.
- Evidence QA is distinct from Product QA.
- Evidence approval does not itself authorize recommendation use.
- UNKNOWN and CONFLICT remain explicit; no unsupported assertion is promoted by summarization or page-level approval.
- No parallel Evidence repository or duplicate knowledge bank is created.
- The current append-only Evidence mutation audit is traceability, not proof of a complete immutable revision/version chain.

## Implementation boundary

This document records the architecture decision only. Runtime code, APIs, UI, schema, migrations, production data, ProductKnowledge, Evidence QA, Inventory, G8 and Recommendation behavior are unchanged by this documentation record.
