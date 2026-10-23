# WP-SKIN-PRODUCT-KNOWLEDGE-STATUS-001 — Conservative status derivation

**Status:** Implementation proposal on an unmerged branch  
**Base:** `cc7848e472b837746e99103ea94ff4bb28eb0c2b`  
**Scope:** ProductKnowledge.evidence_status writer only; no schema, migration, ranking, or product eligibility changes.

## Deterministic rebuild rule

Every call to `ProductKnowledgeService.update_from_evidence(product_id)` derives and persists `ProductKnowledge.evidence_status`:

| Condition | Result |
|---|---|
| Any product Evidence row has `conflict_status=CONFLICT` | `CONFLICT` |
| No Evidence rows pass the existing QA gate (`APPROVED` or `VERIFIED`) and non-conflict filter | `UNKNOWN` |
| At least one row passes that gate and no unresolved conflict exists | `PARTIAL` |

Conflict has precedence, including when the conflicting row itself is pending. Pending/rejected/conflicting rows remain excluded from aggregated ProductKnowledge fields.

## Safety interpretation

- `UNKNOWN` means no currently eligible Evidence was available to this rebuild; it does not mean safe.
- `CONFLICT` means at least one unresolved conflict remains on the product's Evidence set.
- `PARTIAL` means some QA-approved/non-conflicting information is present; it does **not** assert clinical efficacy or independent scientific support.
- `SUPPORTED` is not assigned automatically by this change. QA approval, a manufacturer statement, ingredient presence, or an evidence-strength label alone is not a contract-defined sufficiency rule for finished-product efficacy.

This intentionally conservative rule closes the stale/unset status writer gap without inventing a scientific sufficiency threshold. A future change that assigns `SUPPORTED` requires an explicit acceptance rule and focused tests.

## Verification required

Focused regression tests assert derivation and persisted readback for UNKNOWN, PARTIAL, and CONFLICT. Exact-head GitHub Actions must pass before this work is treated as verified. This change does not merge PR #353 or #357 and does not establish G8 readiness.
