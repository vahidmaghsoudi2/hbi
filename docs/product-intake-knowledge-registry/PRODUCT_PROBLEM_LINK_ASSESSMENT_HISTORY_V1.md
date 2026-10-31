# ProductProblemLink Assessment History V1

Status: implementation proposal on an isolated branch; not merged or deployed.

## Contract

- An assessment proposition is anchored to Product, feature/claim basis, outcome, canonical problem and definition version, relationship role, variant and market.
- feature_basis states the exact feature/claim basis from the selected Evidence record. S01-S10 are problem-bank shelves and must never be used as product-feature identifiers.
- outcome is explicit and separate from the feature/evidence basis. It describes the endpoint being evaluated, not a diagnosis or recommendation.
- assertion_key hashes the complete proposition identity. revision_no versions repeated assessments of the same proposition. If feature basis, outcome, Evidence/Claim or problem-map version changes, the successor starts a new assertion revision series but remains connected through supersedes_link_id.
- Reassessment creates a new ProductProblemLink row and points supersedes_link_id to the prior row. No ordinary update/delete path exists.
- NOT_LINKED means insufficient basis for this proposition and scope; it is not a universal finding that the product has no effect.
- SUPPORTED remains unavailable. No Product Master lifecycle, ProductKnowledge, suitability, or Recommendation state is changed.

## Retry, concurrency and audit

- Every API write requires a caller-supplied idempotency_key; the server stores a request fingerprint. Same key/same payload returns the original assessment; same key/different payload conflicts.
- Reassessment supplies expected_revision_no. Stale revisions conflict; the unique assertion_key/revision_no constraint is the final race guard.
- Assessment row and ProductProblemLinkAssessmentEvent are flushed in the same SQLAlchemy session and committed by the router in one transaction.
- Events record authenticated actor, role, timestamp, reason, and before/after snapshots. Normal application routes expose read-only history and provide no event update/delete operation. This is append-only through normal application paths, not a claim of tamper-proof storage.
- Legacy rows are preserved with NULL feature_basis, outcome, assertion_key, and revision_no; no reviewer, version, or decision is fabricated. A legacy row can be superseded by the first governed revision, which starts at revision 1 and explicitly references the legacy row.

## Migration and deployment

- Fresh databases receive the new model schema through Base.metadata.create_all.
- Existing SQLite databases must run python scripts/migrate_product_problem_link_assessments.py --db data/hbi.db before deploying the matching application code. The script makes a backup, rebuilds the table to remove the old scope-only unique constraint, preserves legacy rows, creates the event table, verifies row counts and foreign keys, and is rerunnable.
- The migration script is SQLite-specific. A PostgreSQL deployment must not use it; an equivalent reviewed PostgreSQL migration is required first.
- No production database was accessed or migrated by this branch. No Recommendation or UI integration is included.
