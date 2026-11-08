# Evidence.packaging_version semantics (Gap C)

**PO decision:** 2026-11-08 — APPROVED WITH ARCHITECTURAL CONSTRAINTS  
**Scope:** additive nullable `Evidence.packaging_version` only.

## Distinction

- **Packaging version** identifies the physical/package presentation of an assertion.
- **Formula version** is a separate concept and is **not** introduced by this change.
- Never treat packaging_version as formula identity.

## Scope key

`version_scope_key` builds: `market={MARKET}|pack={PACK}`

| Evidence.packaging_version | Resolved PACK segment |
|---|---|
| Explicit non-empty string | That string (wins) |
| NULL / empty (legacy) | Product.packaging_version for **scope matching only** |

Legacy inheritance is **read-time grouping only**. Historical Evidence rows are never back-filled.

## Aggregation

- Preferred ProductKnowledge scope uses Product market + Product packaging.
- Evidence in preferred scope contributes content when QA-evaluated.
- Evidence in a different packaging scope does not inject content; approved/conflict signals may mark the domain PARTIAL.
- Different packaging scopes never silently merge content.

## Conflicts

Conflict detection groups by `(field, market_region, packaging_scope)`.

- Same field + same market + same packaging scope + different claim values → CONFLICT candidates.
- Different packaging scopes → **no** cross-version CONFLICT.

## Migration

- File: `scripts/migrations/20261108_evidence_packaging_version.sql`
- Additive `ALTER TABLE … ADD COLUMN packaging_version VARCHAR NULL`
- No production execution without explicit PO authorization.
