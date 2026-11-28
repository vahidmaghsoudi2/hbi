# Anua Evidence Audit — Execution Handoff

**Date:** 2026-11-24  
**Product:** `HBI-PROD-22C55A8223A945A6`  
**Product:** Anua — Azelaic Acid 10% + Hyaluron Redness Soothing Serum  
**Branch:** `agent/chatgpt-gpt6/anua-identity-evidence-record/202611240900`  
**PR:** #655 (must remain Draft and open)

## Scope and safety boundary

This audit is a source-code and recorded-handoff review only. The live SQLite database at `E:\HBI_GitHub_Current\data\hbi.db` and the API at `http://127.0.0.1:8000` are not accessible through the GitHub connector runtime used for this pass. No live Evidence rows were read or changed, no ProductKnowledge refresh was executed, and no application tests were run. Do not interpret this document as evidence of a database mutation.

Do not change the database schema, migrations, product identity, QA state, product lifecycle state, or existing audit rows. Do not delete duplicate evidence. Keep `identity_status=VERIFIED`, `identity_confidence=0.9`, `qa_verdict=PENDING`, and `status=DRAFT` as recorded unless a separate authorized gate changes them.

## Six-record audit register

The current continuity report identifies six records by stable ID suffix. Full IDs and live row values must be re-read from the API before any write.

| Record suffix | Recorded meaning | Required handling before any mutation |
|---|---|---|
| `2b4c9e26` (001) | Manufacturer claim for 10% azelaic acid; a duplicate was noted | Compare full evidence IDs, claim IDs, source references, market scope, QA and conflict states. Preserve both rows and all audit history until an explicit reconciliation decision is justified. |
| `1ed73fb7` (002) | Manufacturer ingredient declaration; PO verification recorded | Preserve manufacturer attribution. Distinguish QA review state from evidence strength/status. |
| `36d28c8a` (003) | Manufacturer test/label claims; public methodology not disclosed | Keep the statement bounded to what the manufacturer says. Do not convert it into independent clinical efficacy or a substantiated clinical outcome. |
| `1d858e1c` (004) | Usage guidance; encoding defect reported | Recover exact source wording first. Repair text encoding only; do not paraphrase directions or alter dosage/frequency. Package directions remain authoritative. |
| `3b14ff45` (005) | Ingredient-role inference | Keep explicitly inferential. Never classify or aggregate it as a manufacturer claim. Preserve its role semantics and provenance. |
| `526fa458` (006) | Separate routine-page participant-agreement claim | Keep scoped to the routine page. Do not attribute it to this serum without product-specific source evidence. |

For records 002–004, the prior local inspection reported `qa_status=VERIFIED`, `evidence_strength=UNVERIFIED`, and `evidence_status=UNKNOWN`. These are independent dimensions and must remain separate.

## Source-code findings

Reviewed on the PR branch:

- `app/api/routers/evidence.py`
- `app/services/evidence_service.py`
- `app/services/evidence_mutation_log_service.py`
- `app/services/product_knowledge_service.py`
- `app/repositories/evidence_repository.py`
- `app/models/product_knowledge.py`

### 1. ProductKnowledge inclusion rule

`ProductKnowledgeService.update_from_evidence()` treats QA values `APPROVED` and `VERIFIED` as approved for content ingestion. The ingestion path does not independently require `evidence_strength` to be above `UNVERIFIED`, nor does it require `evidence_status=SUPPORTED`. Therefore a QA-VERIFIED row can contribute content while its strength remains UNVERIFIED and its evidence status UNKNOWN. This must be explicitly visible in the audit interpretation; QA verification is not a scientific-strength upgrade.

### 2. Market scope

The rebuild derives its preferred market scope from the Product market and requires Evidence to independently carry that same market to enter the primary content scope. Evidence from other or missing scopes is not allowed to inject content into the preferred scope. Keep the Anua product market as US; do not silently backfill Evidence market values without source-backed authorization.

### 3. Manufacturer-claim boundary

The rebuild aggregates fields `manufacturer_claims` / `manufacturer_claim` only when `claim_type=MANUFACTURER_CLAIM`. It also maps field `claim` into manufacturer claims only when the claim type is MANUFACTURER_CLAIM. Record 005 must not cross this boundary. Record 006 must be excluded from product-specific content unless its source and scope prove that it is about this serum.

### 4. Rebuild is destructive to aggregate fields

The rebuild computes aggregate values and calls `update_knowledge()` with every aggregate field, including explicit `None` for empty results. This can clear existing ProductKnowledge values. A refresh must therefore happen only after the complete live Evidence snapshot, source text, scope, QA/conflict state, and audit history have been captured and reconciled.

### 5. Audit trail

Evidence mutations are logged through `EvidenceMutationLogService.append()` with before/after snapshots and action metadata. The log is append-only by service design. Use the dedicated audited reclassification operation for field-only corrections; never edit or delete mutation-log rows. Reclassification is restricted to PENDING Evidence and records a reason. Already VERIFIED records must not be reclassified through that path.

## API readback sequence required before writes

Use the existing local PO authentication workflow and keep the short-lived token only in the local process. Do not put credentials or tokens in GitHub.

1. `GET /api/v1/products/HBI-PROD-22C55A8223A945A6`
2. `GET /api/v1/evidence/?product_id=HBI-PROD-22C55A8223A945A6`
3. `GET /api/v1/evidence/knowledge/HBI-PROD-22C55A8223A945A6`
4. `GET /api/v1/evidence/knowledge/HBI-PROD-22C55A8223A945A6/completeness`
5. `GET /api/v1/evidence/audit/product/HBI-PROD-22C55A8223A945A6`
6. For each of the six full evidence IDs: `GET /api/v1/evidence/{evidence_id}/audit`

Save an immutable before-snapshot locally before any mutation. Compare all six full IDs and the complete set of product Evidence rows; do not assume the six listed rows are the only rows attached to the product.

## Mutation and refresh gates

- Do not mutate until the full readback and source-text comparison are complete.
- A field-only reclassification is permissible only for a PENDING row, using `POST /api/v1/evidence/{evidence_id}/reclassify` with the exact target field and a factual reason. This endpoint does not change QA status.
- Do not change `claim_type`, source attribution, market scope, QA status, evidence strength, or evidence status merely to make the aggregation look clean.
- Do not resolve or delete the duplicate claim unless source reconciliation establishes the correct governance outcome and the authorized operation is clear.
- After any approved mutation, re-read the row and its audit log; verify the before/after and reason.
- Refresh only after all six records and any other product-linked Evidence have been reconciled. The refresh endpoint is `POST /api/v1/evidence/knowledge/{product_id}/refresh`. Capture its response and immediately GET ProductKnowledge and completeness again.
- Confirm that `known_use_cases` and `contraindications` remain unknown/null unless product-specific authoritative evidence supports them.
- Confirm usage text is correctly encoded and no routine-only claim or inference is misrepresented as manufacturer content.

## Test and evidence status

- GitHub source review: performed for the files listed above.
- Live database/API readback: **not performed in this runtime**.
- Evidence mutation: **not performed**.
- ProductKnowledge refresh: **not performed**.
- Automated tests: **GitHub Actions CI passed** on commit `86ad8f512e6bc87d2915c0adeb3c8f8d8fffb7e9` (run `45279455883`). The `test` job completed compile checks, G8 regression bundle, pytest with strict coverage, and frontend typecheck/build successfully. The `governance-tests` job passed the P4 compliance and API auth matrix suites. The `g8-isolated-pilot-smoke` job passed API startup/health against a disposable SQLite database. These results do not validate the live Anua database or the six Evidence rows.
- Browser proof: run `45279455803`; 61-record parser conformance and isolated fixture preparation passed. The real-browser proof step was still `in_progress` at the time of this update; no final browser result is claimed.
- Live local API/SQLite tests: **not run**.
- Schema/migration changes: **none**.
- Merge/review: **not performed**. PR #655 remains Draft and open.

## Next execution requirement

Continue from the local HBI runtime that owns `E:\HBI_GitHub_Current\data\hbi.db` and `http://127.0.0.1:8000`. This GitHub-only runtime cannot read that loopback service or the gitignored SQLite file. Do not substitute guesses, seeded data, or repository fixtures for the live database. Once actual readback and approved mutations are available, append the exact outputs, IDs, timestamps, reasons, and test commands/results to the final report on this same branch and PR.
