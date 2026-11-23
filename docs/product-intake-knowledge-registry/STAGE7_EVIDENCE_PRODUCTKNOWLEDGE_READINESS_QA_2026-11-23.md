# Stage 7 — Evidence & ProductKnowledge Readiness QA (Read-only)

**Status:** Audit completed; remediation candidates documented; no operational mutation authorized or performed.  
**Accepted input:** Stage 6 research reconciliation accepted by PO in the conversation on 2026-11-23.  
**Inputs:** Stage 5 seven-product baseline and its 2026-11-23 read-only operational snapshot reconciliation; Stage 6 research artifact.  
**Scope:** Field-coverage/readiness audit of the seven canonical product dossiers and their reported ProductKnowledge/Evidence snapshot, strictly read-only.  
**Not in scope:** Live DB access, re-query/export, writes, Evidence QA-state transitions, ProductKnowledge rebuilds, product activation, physical package authentication, merge, deployment, or Stage 8.

## QA rules

1. Audit against the pinned Stage 5 snapshot only. This is not a fresh operational query.
2. Evidence rows with UNKNOWN status, UNVERIFIED strength, or PENDING/NEEDS_REVIEW QA remain unaccepted.
3. Field coverage does not establish factual accuracy, physical package match, or evidence sufficiency.
4. Do not delete, merge, rewrite, reclassify, or flag-clear existing Anua rows.
5. Manufacturer disclosures and claims remain source-scoped; ingredient roles remain inferences.
6. ProductKnowledge payloads are not eligible to be promoted to approved/accepted knowledge merely because fields are populated.
7. Any remediation proposal must be separately reviewed and explicitly authorized before data mutation.

## Snapshot-level results (pinned Stage 5 report; not independently refreshed)

- Canonical Product: 7.
- ProductKnowledge: 7.
- Evidence: 25.
- Inventory: 7 rows, 12 each / 84 planning units.
- Evidence strength: UNVERIFIED (25/25).
- Evidence status: UNKNOWN (25/25).
- Conflict status: NONE (25/25), including the Anua flag discrepancy documented below.
- QA status: 19 PENDING, 6 NEEDS_REVIEW.
- Product status/identity/QA: all DRAFT / NEEDS_REVIEW / PENDING in the reported snapshot.
- SQLite integrity: `ok`; foreign-key violations: 0.
- Operational source hash was reported to match the prior identified fingerprint; export timestamp remains future-dated relative to the report date and is an open provenance caveat.

These are report facts from the pinned snapshot, not live-state claims.

## Product-level field-coverage audit

| Product | Evidence rows vs manifest | ProductKnowledge payload | Readiness outcome |
|---|---:|---|---|
| P1 COSRX | 4 / 4, field counts align | Payload fields and evidence_refs all NULL | **BLOCKED — missing payload/reference mapping** |
| P2 Neutrogena | 4 / 4, field counts align | Ingredients, ingredient_roles, usage_instructions, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P3 Garnier | 3 / 3, field counts align | Ingredients, ingredient_roles, known_use_cases, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P4 SKIN1004 | 3 / 3, field counts align | Ingredients, ingredient_roles, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P5 ISDIN | 2 / 2, field counts align | manufacturer_claims, known_use_cases, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P6 Clinique | 3 / 3, field counts align | Ingredients, ingredient_roles, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P7 Anua | 6 / 5, duplicate ingredients field | Payload fields and evidence_refs all NULL | **BLOCKED — payload gap plus open conflict** |

Coverage pass means only that the stored field names/counts appear to map to the staged assertion inventory in the pinned snapshot. It is not evidence acceptance.

## Remediation candidate ledger

| ID | Priority | Product / area | Candidate action | Prerequisite / stop condition |
|---|---|---|---|---|
| R-01 | P0 | P7 Anua duplicate ingredients Evidence | Human row-to-source mapping review; document which assertion is which, without changing rows | Must reconcile the two rows, manifest conflict note, and both stored `conflict_status=NONE`; no auto-merge/delete |
| R-02 | P0 | P7 Anua ProductKnowledge | Draft mapping plan only after R-01; do not build payload yet | Source/market/package scope and conflict disposition must be explicit; any new source is separately reviewed |
| R-03 | P1 | P1 COSRX ProductKnowledge | Draft field-to-Evidence mapping and missing-payload report | Physical target identity remains UNKNOWN; avoid populating fields beyond the source-supported assertions |
| R-04 | P1 | P1 evidence_refs | Establish traceable mapping from four Evidence rows to payload fields | IDs/row-level snapshot are not in this artifact; no guessed IDs |
| R-05 | P2 | P2–P6 ProductKnowledge review | Validate each populated field maps to correct Evidence/source and respects claim taxonomy | Need row-level export and source mapping; coverage is not QA approval |
| R-06 | P2 | All 7 ProductKnowledge | Keep evidence_status UNKNOWN and confidence 0.0 until QA gate is passed and PO-approved state transition is defined | No status/confidence changes in this Stage |
| R-07 | P2 | Product Master metadata | Review size/source-market metadata gaps (P1 size, P4 market/size, P5 market/size, P6 market, P7 market) | Source markets cannot be promoted to physical package identity; package/GTIN evidence needed for physical identity |
| R-08 | P2 | Snapshot provenance | Confirm future-dated export timestamp/host clock/timezone or produce corrected timestamped read-only export if needed | This document does not request a new export unless PO deems timestamp material |

## Cross-cutting safety decisions

- No candidate is an automatic mutation.
- Do not infer physical identity from manufacturer web pages or source markets.
- P4 international/Korean and US formulas remain separate.
- P6 historical Clinique and replacement remain separate.
- P7 serum and pads remain separate.
- Claims remain MANUFACTURER_CLAIM; ingredient-role mapping remains INFERENCE.
- Existing UNKNOWN, CONFLICT, PENDING, NEEDS_REVIEW labels are preserved.
- Inventory planning remains 12 each / 84 from the accepted snapshot; no physical stock count or sellability claim is made.
- Recommendation and ProductProblemLink are empty in the snapshot; this QA stage does not invent relationships.

## Stage 7 acceptance criteria

- [x] Stage 6 accepted input recorded.
- [x] Snapshot-level counts and classifications transcribed from pinned Stage 5 reconciliation.
- [x] All seven ProductKnowledge field-coverage states compared with the manifest.
- [x] P1 and P7 payload/reference gaps identified.
- [x] P7 duplicate-row/conflict-flag discrepancy preserved as OPEN.
- [x] Remediation candidates and prerequisites documented.
- [x] All non-acceptance labels and source/version boundaries preserved.
- [x] No DB/API/runtime write or mutation performed.
- [ ] PO review of Stage 7 QA artifact.
- [ ] Row-level Evidence IDs/source mappings inspected from an authorized read-only export before any remediation design.
- [ ] Separate explicit authorization for any Evidence/ProductKnowledge mutation, QA transition, activation, or import.

## Disposition

**Stage 7 read-only readiness QA: COMPLETE.**  
**Operational remediation: NOT STARTED / NOT AUTHORIZED.**  
**Evidence acceptance: NONE.**  
**ProductKnowledge acceptance: NONE.**  
**Stage 8: NOT STARTED.**

The next safe action is a row-level source-to-Evidence mapping review using a permitted read-only export, focusing first on P7 and P1. This would still be review-only; no mutation follows automatically.


## Export-tool / runbook review (read-only source inspection)

The existing PR #523 exporter and Windows PowerShell runbook were inspected as source code; they were **not executed** in this session because execution requires the operator's local database path and machine.

Source-reviewed safeguards:
- The exporter uses an allowlist for seven canonical product IDs and selected columns from Product, Evidence, ProductKnowledge, Inventory, Recommendation, and ProductProblemLink.
- It does not open the source DB in SQLite; it hashes source DB/sidecars, copies DB plus WAL to an isolated temp path, then opens the copy read-only/query-only.
- It rejects symlink sources, existing output overwrite, rollback journals, source changes during copy, and output paths that target source DB/sidecars.
- It records structural integrity, foreign-key count, missing IDs/tables/columns, and row counts.
- The runbook checks source hashes before/after, exporter exit code, integrity, FK violations, missing product IDs/tables/columns, and advises quarantining incomplete output.
- It explicitly warns that a successful export is not product acceptance or E2E.

**Operator boundary:** no local database path was supplied or accessed, and the exporter was not run. A row-level export is still required for the next mapping-review task. The JSON should be reviewed privately before sharing; it is product-scoped but includes claims and source references.
