# Product Acceptance Report Contract v1.0.0 — DRAFT

**Status:** IMPLEMENTATION-ALIGNED DRAFT — Product Owner review required  
**Scope:** Read-only reporting contract for the Product Acceptance Report API  
**Implementation:** PR #582  
**Not authorized by this document:** schema/migration changes, Evidence QA changes, Product QA/lifecycle transitions, recommendation/scoring changes, activation, or merge.

This document records the response currently implemented by PR #582. It is not a claim that the Product Owner has frozen or accepted the contract. Any semantic change to the response must be reviewed against this document before implementation.

## 1. Purpose and non-purpose

The report assembles a traceable snapshot of Product identity, Product QA, Evidence QA, audit history, ProductKnowledge storage, and known data limitations.

It is a governance/inspection report. It is **not**:
- a product recommendation or customer suitability decision;
- an approval or activation command;
- a clinical efficacy assessment;
- proof that a manufacturer claim is independently established;
- proof that a product's stored knowledge fields are supported by eligible Evidence.

The report is read-only. It must not create, update, delete, promote, or transition Product, Evidence, ProductKnowledge, inventory, or lifecycle records.

## 2. API surface

### 2.1 Single product

`GET /api/v1/products/{product_id}/acceptance-report`

- Required role: Reviewer/QA, PO, or Admin.
- Returns one report for an existing Product.
- Returns 404 when Product does not exist.
- Returns 503 when the report source is unavailable.

### 2.2 Cohort

`POST /api/v1/acceptance-reports/cohort`

Request:
- `product_ids`: required array, 1–500 unique non-empty strings, each at most 128 characters.
- `cohort_label`: optional string, at most 120 characters.
- `include_evidence_details`: optional boolean, defaults to true.
- Unknown request properties are rejected.

Required role: Reviewer/QA, PO, or Admin.

The cohort response preserves request order for successfully built reports, lists missing IDs separately, and isolates per-product build errors. A shared source failure may fail the cohort request.

## 3. Readiness semantics

Single-product `evidence_readiness`:

| Value | Meaning |
|---|---|
| `NOT_ASSESSED` | No Evidence rows exist for the Product. |
| `READY` | Every Evidence row is eligible under the current report policy. |
| `PARTIAL` | At least one Evidence row is eligible, but not all are. |
| `BLOCKED` | Evidence rows exist and none is eligible. |

Eligibility is conjunctive. At minimum, the Evidence row must have:
- QA status exactly `VERIFIED` (not `APPROVED`);
- conflict status exactly `NONE` or `RESOLVED`;
- a recognized Knowledge field;
- non-empty claim, allowed claim type, source type, and source reference;
- applicable market scope;
- an explicit Evidence-level formula/version scope.

**Current implementation limitation:** the Evidence model has no formula/version scope field. Therefore every Evidence row currently receives `EVIDENCE_VERSION_SCOPE_UNAVAILABLE` and scope `UNKNOWN` (unless market mismatch yields `MIXED`). As a result, the current implementation deliberately does not mark such Evidence eligible. `Product.packaging_version` does not establish Evidence applicability.

Product identity status, Product QA verdict, Product lifecycle status, Evidence QA, and ProductKnowledge are separate dimensions. None substitutes for another.

## 4. Single-product response

Top-level fields:

| Field | Type | Meaning / source |
|---|---|---|
| `schema_version` | string | Response contract marker; currently `1.0.0`. |
| `report_id` | string | Generated report identifier. |
| `generated_at` | ISO-8601 string | UTC report generation time. |
| `source_data_timestamp` | ISO-8601 string or null | Latest available Product, ProductKnowledge, Evidence creation, or relevant audit timestamp. |
| `source_data_timestamp_status` | enum | `KNOWN` or `UNKNOWN`. |
| `report_status` | string | `COMPLETED` for a successfully assembled product report. |
| `evidence_readiness` | enum | Readiness semantics in §3. |
| `product` | object | Product identity, QA, lifecycle, market and packaging metadata. |
| `evidence_summary` | object | Counts of Evidence QA/conflict/eligibility states. |
| `evidence` | array | Per-Evidence details and audit history. |
| `knowledge` | object | Stored ProductKnowledge presence and field-level support summary. |
| `data_availability` | object | Availability of audit tables and version-scope model attributes. |
| `limitations` | string array | Known limitations that constrain interpretation. |

### 4.1 Product object

- `product_id`, `brand`, `product_name`: Product Master identity.
- `identity_status`, `qa_verdict`, `lifecycle_status`: separate Product governance states.
- `market_region`, `packaging_version`: Product Master metadata; packaging version is not an Evidence applicability link.
- `product_qa.qa_reviewed_at`, `product_qa.qa_notes`: Product QA metadata.
- `product_qa.qa_decision_history`, `latest_qa_decision`: available Product mutation audit records with action `QA_CHANGE`.

Each QA decision record may contain `audit_record_id`, `audit_timestamp`, `actor`, `role`, `decision`, `reason`, `reason_status`, and Product QA `qa_notes`.

### 4.2 Evidence summary

Counts:
`total`, `verified`, `pending`, `needs_review`, `rejected`, `conflicting`, `unknown_conflict`, `eligible`, `ineligible`, `unknown_scope`.

These are counts, not an overall Product approval verdict.

### 4.3 Evidence item

Each item contains:
- identity/content: `evidence_id`, `field`, `claim`, `claim_type`;
- provenance: `source_type`, `source_reference`, `market_region`;
- governance: `qa_status`, `conflict_status`;
- applicability: `scope_status`, `eligible`, `eligibility_reasons`;
- audit: `qa_decision_history`, `latest_qa_decision`, `qa_decision_history_status`.

Scope statuses currently used:
- `UNKNOWN`: applicability cannot be established, including missing Evidence-level formula/version scope.
- `MIXED`: Evidence market and Product market explicitly differ.

Eligibility reasons are machine-readable blockers, including but not limited to:
`QA_STATUS_NOT_VERIFIED`, `CONFLICT_UNRESOLVED`, `CONFLICT_STATUS_UNKNOWN`, `INVALID_OR_UNKNOWN_FIELD`, `CLAIM_MISSING`, `CLAIM_TYPE_MISSING`, `CLAIM_TYPE_INVALID`, `SOURCE_TYPE_MISSING`, `SOURCE_REFERENCE_MISSING`, `MARKET_SCOPE_UNKNOWN`, `MARKET_SCOPE_MISMATCH`, and `EVIDENCE_VERSION_SCOPE_UNAVAILABLE`.

Audit history status:
- `CONSISTENT`: available matching QA decision history is present.
- `INCOMPLETE`: available history does not fully explain the current state, including conflict-resolution side effects without a per-row event or a VERIFIED event without a reason.
- `NO_RECORDED_DECISION`: a decision-like current state exists but no matching decision history is present.
- `NO_DECISION_RECORDED`: no decision-like current state is recorded.
- `UNAVAILABLE`: the Evidence audit table is unavailable.

The report must never fabricate a missing audit event or reason.

### 4.4 Knowledge object

- `record_exists`: whether a ProductKnowledge row exists.
- `evidence_status`, `knowledge_confidence`, `domain_evidence_status`, `evidence_refs`: stored ProductKnowledge metadata.
- `stored_content_fields`: non-empty fields stored in ProductKnowledge.
- `verified_content_fields`: canonical fields backed by currently eligible Evidence.
- `contraindications_status`: `VERIFIED` only when an eligible contraindications Evidence exists; otherwise `UNVERIFIED` when text is stored, or `UNKNOWN` when no value is stored.

Stored text must not be represented as verified merely because it exists.

### 4.5 Data availability and limitations

Data availability reports:
`product_qa_audit_available`, `evidence_audit_available`, `evidence_market_scope_available`, `evidence_formula_version_available`, `product_packaging_version_available`, `product_packaging_version_value_present`, and `product_version_proves_evidence_scope`.

The final flag is currently always false by design.

Limitations are explanatory constraints, not warnings that can be ignored to force readiness.

## 5. Cohort response

Top-level fields:
- `schema_version`, `cohort_label`, `report_status`;
- `requested`, `found`, `missing`, `successfully_reported`, `failed`;
- readiness counts: `ready`, `partial`, `blocked`, `not_assessed`;
- `missing_product_ids`, `failed_products`, `reports`.

Invariants:
- `requested = found + missing`
- `found = successfully_reported + failed`
- `successfully_reported = ready + partial + blocked + not_assessed`

`report_status` is:
- `COMPLETED` when every requested Product was reported;
- `COMPLETED_WITH_ERRORS` when any requested Product is missing or its report failed;
- `FAILED` when no report was successfully built and at least one build failed.

When `include_evidence_details=false`, per-product `evidence` arrays are empty; summary and other report sections remain.

## 6. Security, privacy and read-only requirements

- Both endpoints require Reviewer/QA, PO, or Admin.
- Cohort request rejects duplicate IDs, blank IDs, overlong IDs, and extra properties.
- The service uses reads only. No state transition or mutation is part of report generation.
- Error messages for per-product failures do not expose exception details.
- Audit history is read from existing mutation logs; unavailable or incomplete history remains visible.

## 7. Known gaps and decisions not made

1. Evidence formula/version applicability has no approved data model. The implementation remains fail-closed. Any new model requires a separate PO decision, migration/backfill policy, and audit requirements.
2. Product Intake V1 leaves complex history/version schema OPEN; this report does not close that item.
3. The current report marker `1.0.0` describes the implementation shape, not independent PO acceptance of this draft.
4. The report does not establish customer-specific suitability, recommendation readiness, activation, or G8 acceptance.

## 8. Acceptance checklist for Product Owner review

- [ ] Confirm the purpose and non-purpose in §1.
- [ ] Accept or revise readiness semantics in §3.
- [ ] Accept the single-product field/source mapping in §4.
- [ ] Accept cohort fields and invariants in §5.
- [ ] Confirm role and read-only requirements in §6.
- [ ] Confirm the fail-closed version-scope limitation in §7.
- [ ] Decide separately whether a future Evidence formula/version scope WP should be opened.

Until these items are explicitly accepted, this document remains a draft and PR #582 must not be represented as having a frozen Product Owner response contract.
