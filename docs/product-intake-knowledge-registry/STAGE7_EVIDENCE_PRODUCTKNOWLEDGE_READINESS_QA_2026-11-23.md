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
| P1 COSRX | 4 / 4, field counts align | ingredients, ingredient_roles, known_use_cases, manufacturer_claims and evidence_refs populated and row-linked | **COVERAGE PASS; NOT ACCEPTED** |
| P2 Neutrogena | 4 / 4, field counts align | Ingredients, ingredient_roles, usage_instructions, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P3 Garnier | 3 / 3, field counts align | Ingredients, ingredient_roles, known_use_cases, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P4 SKIN1004 | 3 / 3, field counts align | Ingredients, ingredient_roles, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P5 ISDIN | 2 / 2, field counts align | manufacturer_claims, known_use_cases, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P6 Clinique | 3 / 3, field counts align | Ingredients, ingredient_roles, manufacturer_claims, evidence_refs populated | **COVERAGE PASS; NOT ACCEPTED** |
| P7 Anua | 6 / 5; snapshot stores one `ingredients` row and two `manufacturer_claims` rows | Payload fields and evidence_refs all NULL | **BLOCKED — one redundant manufacturer-claim row plus missing payload** |

Coverage pass means only that the stored field names/counts appear to map to the staged assertion inventory in the pinned snapshot. It is not evidence acceptance.

## Remediation candidate ledger

| ID | Priority | Product / area | Candidate action | Prerequisite / stop condition |
|---|---|---|---|---|
| R-01 | P0 | P7 Anua extra Evidence row | `...-001` is the redundant narrow 10% claim; `...-003` carries the same 10% claim plus non-comedogenic/low-irritation labels from the same official page. Preserve `...-002` as the sole ingredients row. | Before deletion, inspect all FK/reference/audit dependencies for `...-001`; remove only that exact redundant row through an authorized application/service path. Never delete `...-002` or `...-003`. |
| R-02 | P0 | P7 Anua ProductKnowledge | After R-01, build the five manifest-aligned fields and `evidence_refs` from `...-002`, `...-003`, `...-004`, `...-005`, `...-006`. Keep `ingredient_roles` as INFERENCE and all manufacturer statements as MANUFACTURER_CLAIM. | Source/market/package scope must be explicit; use the physical label if its market/INCI differs. No confidence or QA promotion without separate acceptance. |
| R-03 | P2 | P1 COSRX ProductKnowledge | No payload-gap remediation indicated by the pinned JSON: four populated fields map to four Evidence rows | Physical target identity remains UNKNOWN; do not infer 150 ml package identity from the research target |
| R-04 | P2 | P1 evidence_refs | Pinned JSON contains all four exact Evidence IDs in evidence_refs and in their corresponding payload fields | No mutation; revisit only if a newer authoritative snapshot contradicts this artifact |
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
- [x] P7 payload/reference gap identified; P1 payload and all four Evidence references verified as populated and aligned.
- [x] P7 manifest/snapshot field-mapping and conflict-flag discrepancies preserved as OPEN.
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

The next safe action is human row-lineage reconciliation for P7 using the pinned manifest and snapshot, followed by any source-mapping questions that remain for P2–P6. P1's mapping is already structurally aligned in this artifact. This remains review-only; no mutation follows automatically.


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


## 2026-11-23 — Row-level snapshot mapping audit and correction

**Correction / supersession:** the P1 statements in the initial QA table and remediation ledger above were incorrect. Re-reading the exact Stage 5 JSON artifact `hbi-stage5-snapshot-20261124-235415.json` shows that P1 COSRX ProductKnowledge is populated and all four Evidence IDs are present in both the corresponding field payloads and `evidence_refs`. The corrected P1 result is **COVERAGE PASS; NOT ACCEPTED**, not a payload gap. R-03/R-04 above are superseded by the corrected descriptions. No data was changed.

### Snapshot identity and integrity (file-level)
- File: `hbi-stage5-snapshot-20261124-235415.json` (64,473 bytes; 893 lines).
- JSON `exported_at_utc`: `2026-11-24T20:24:16+00:00`.
- Source DB SHA-256: `cb75363628cf3dd8320d5b40c324276b018b3075a18489b4ba4f1420fd541d1c`, matching the fingerprint recorded in the Stage 5 addendum.
- `integrity_check=ok`; foreign-key violations 0; missing canonical Product IDs/tables/columns all empty.
- **Timestamp remains a blocker for freshness claims:** the export timestamp and filename are future-dated relative to this 2026-11-23 review. The Library file metadata says it was created 2026-11-22, which does not resolve the content timestamp discrepancy. This artifact is treated only as the pinned Stage 5 content under review, not as a fresh 2026-11-23/24 operational readback.

### Row-level Evidence-to-ProductKnowledge mapping

All row IDs below are copied from the JSON snapshot. The audit compared each Evidence row's `evidence_id`, `claim_id`, `field`, `claim_type`, `source_type`, `market_region`, `qa_status`, and `conflict_status` with the corresponding ProductKnowledge payload references and `evidence_refs`.

| Product | Evidence rows and field mapping | ProductKnowledge field mapping | Result |
|---|---|---|---|
| P1 COSRX | `87b3c09a` ingredients; `0af6e231` ingredient_roles; `22f74e31` manufacturer_claims; `7798e9e2` known_use_cases | All four fields populated with the matching Evidence IDs; `evidence_refs` contains the same four IDs | **MATCH; NOT ACCEPTED** |
| P2 Neutrogena | `f525337a` ingredients; `b730645d` manufacturer_claims; `69df6282` ingredient_roles; `d956ff00` usage_instructions | All four corresponding fields populated; `evidence_refs` contains the same four IDs | **MATCH; NOT ACCEPTED** |
| P3 Garnier | `993c35d8` ingredients; `bfa851e2` ingredient_roles; `9cf6c4dd` known_use_cases | All three corresponding fields populated; `evidence_refs` contains the same three IDs | **MATCH; NOT ACCEPTED** |
| P4 SKIN1004 | `ab707983` ingredients; `bd9c4e47` ingredient_roles; `83a368c1` manufacturer_claims | All three corresponding fields populated; `evidence_refs` contains the same three IDs | **MATCH; NOT ACCEPTED** |
| P5 ISDIN | `982bc851` manufacturer_claims; `c45194ac` known_use_cases | Both corresponding fields populated; `evidence_refs` contains the same two IDs | **MATCH; NOT ACCEPTED** |
| P6 Clinique | `274f20c2` ingredients; `307d2efe` manufacturer_claims; `4f48ff5b` ingredient_roles | All three corresponding fields populated; `evidence_refs` contains the same three IDs | **MATCH; NOT ACCEPTED** |
| P7 Anua | `2b4c9e26` manufacturer_claims; `1ed73fb7` ingredients; `36d28c8a` manufacturer_claims; `1d858e1c` usage_instructions; `3b14ff45` ingredient_roles; `526fa458` claimed_benefits | All ProductKnowledge payload fields and `evidence_refs` are NULL | **BLOCKED; manifest-to-snapshot field mismatch and conflict note remain OPEN** |

The suffixes in the table are abbreviated for readability; each full Evidence ID is `EV-HBI-PROD-{ProductID}-{suffix}`, with the ProductID corresponding to the row's canonical dossier. No IDs were inferred or generated.

### Cross-row findings
- P1–P6: Evidence row counts and fields align with the corresponding ProductKnowledge payload field references; each ProductKnowledge `evidence_refs` set exactly matches its Evidence row set.
- P7: six Evidence rows versus five manifest assertions. The snapshot has one `ingredients` row (`1ed73fb7`) and two `manufacturer_claims` rows (`2b4c9e26`, `36d28c8a`). The narrower `manufacturer_claims` row `2b4c9e26` (claim `...-001`) is redundant because `36d28c8a` (claim `...-003`) includes the same 10% declaration plus the testing labels. The manifest's note about two `ingredients` rows is inaccurate. `1ed73fb7` is the sole ingredients row and must be preserved.
- All 25 Evidence rows remain `UNVERIFIED` / `UNKNOWN`; 19 are `PENDING`, six are `NEEDS_REVIEW`; all stored `conflict_status` values are `NONE`. No status was promoted.
- All seven ProductKnowledge rows remain `evidence_status=UNKNOWN`, `knowledge_confidence=0.0`, and `domain_evidence_status=NULL`.
- Product Master remains DRAFT / NEEDS_REVIEW / PENDING across all seven records. Recommendation and ProductProblemLink remain empty.

### Revised readiness disposition
- P1–P6: row-level coverage/reference mapping matches within this pinned JSON; this is structural mapping only, not evidence QA acceptance, factual verification, physical package identity, or consultation readiness.
- P7: payload is entirely absent. One `manufacturer_claims` row (`...-001`) is redundant and is the deletion candidate; `...-003` subsumes its 10% claim and adds the testing labels. Preserve the sole ingredients row `...-002`, plus `...-003` through `...-006`. The manifest's duplicate-ingredients note is wrong and must be corrected.
- Stage 7 remains read-only. No Evidence/ProductKnowledge write, QA transition, identity change, activation, import, merge, or Stage 8 work was performed.


### P7 manifest-to-snapshot crosswalk (explicit discrepancy)
- Manifest assertion fields (5): `ingredients`, `manufacturer_claims`, `usage_instructions`, `ingredient_roles`, `claimed_benefits`.
- Manifest identity note: two existing conflicting Evidence rows reportedly use `field=ingredients`.
- Snapshot Evidence fields (6 rows): `manufacturer_claims` for claim IDs `...-001` and `...-003`; `ingredients` for `...-002`; `usage_instructions` for `...-004`; `ingredient_roles` for `...-005`; `claimed_benefits` for `...-006`.
- Therefore the snapshot's field distribution is **not** the same as the manifest's reported duplicate-ingredients distribution. The extra row appears in `manufacturer_claims` in the snapshot, but row lineage and intended assertion identity cannot be established from counts alone.
- No row deletion, merge, field rewrite, reclassification, conflict-flag update, or ProductKnowledge rebuild is permitted by this audit.


---

## 2026-11-24 — Correction of unauthorized P7 exclusion and approved remediation target

**Correction:** The earlier quarantine/exclusion disposition was not authorized by the Product Owner and conflicts with the explicit instruction to keep Anua in the acceptance path. It is superseded in full by this section.

### Final disposition: ACTIVE — REMEDIATION REQUIRED

- P7 Anua serum remains in the active seven-product acceptance path. It is not quarantined, excluded, or removed from intake.
- Preserve the six Evidence rows until exact dependency/reference checks are completed.
- The one redundant row is `EV-HBI-PROD-22C55A8223A945A6-001` (snapshot suffix `2b4c9e26`): it contains only the 10% azelaic-acid manufacturer declaration.
- Keep `EV-HBI-PROD-22C55A8223A945A6-003` (suffix `36d28c8a`): it contains the same 10% declaration plus the non-comedogenic/low-irritation manufacturer testing labels.
- Keep `...-002` (suffix `1ed73fb7`) as the only ingredients record; it contains the US official page's full INCI. The manifest's statement that there are two `ingredients` rows is incorrect.
- Keep `...-004` usage instructions, `...-005` ingredient-role inference, and `...-006` claimed-benefit manufacturer claim.
- The intended five-row set is therefore `...-002`, `...-003`, `...-004`, `...-005`, `...-006`.
- ProductKnowledge is currently empty in the pinned snapshot. Rebuild its five fields and `evidence_refs` only after the redundant-row reference/dependency audit and cleanup.
- No physical package market/lot/GTIN match is inferred from the US website. Any package-specific label information must be recorded as package-sourced evidence for that exact unit/market, without replacing the official US page source.

### Execution boundary

This correction changes the repository's QA/remediation record only. It does not claim that the operational database has been modified. The available GitHub connection cannot execute a transaction against the local SQLite database. Operational cleanup must use the approved application/service path, verify all references and audit requirements, and then produce a fresh read-only snapshot. No direct SQL deletion is authorized by this document.

**Stage 7 disposition:** Anua remains active; duplicate candidate identified; ProductKnowledge rebuild pending authorized operational execution and verification. Evidence acceptance and ProductKnowledge acceptance remain NONE until QA and explicit acceptance are complete.
