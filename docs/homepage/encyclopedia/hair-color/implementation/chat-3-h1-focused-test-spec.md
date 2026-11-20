# H1 Focused Test Specification — Chat 3/6

**Status:** Focused H1 test suite executed twice; H1 acceptance remains PARTIAL pending criterion-level closeout.  
**Gate:** PO authorized isolated H1 validation on 2026-11-20, limited to synthetic/test data and the recorded baseline.  
**Data:** Synthetic fixtures only; no real customer data.  
**Purpose:** Convert static audit findings into executable, bounded acceptance tests without changing runtime behavior.

## Test batch A — Catalog provider and snapshot manifest

| ID | Synthetic setup | Expected assertion |
|---|---|---|
| A01 | Correct 88-row, 19-series CSV + valid manifest + exact digest | Provider returns validated reference; publisher metadata remains null when absent |
| A02 | Row count 87 | Provider returns no reference |
| A03 | Unexpected header / column order | Provider returns no reference |
| A04 | One series omitted or unapproved series inserted | Provider returns no reference |
| A05 | Shade code moved to another series | Provider returns no reference |
| A06 | Duplicate canonical identity | Provider returns no reference |
| A07 | Empty required identity/name | Provider returns no reference |
| A08 | Missing CSV or invalid UTF-8 | Provider returns no reference |
| A09 | Missing manifest, invalid JSON, non-object root | Provider returns no reference |
| A10 | Wrong schema version, source URL, artifact path, capture method or validation policy | Provider returns no reference |
| A11 | Hash mismatch or row/column count metadata mismatch | Provider returns no reference |
| A12 | Missing/invalid snapshot timestamp, naive timestamp | Provider returns no reference |
| A13 | Publisher edition/revision invalid blank type; publisher capture time invalid/naive | Provider returns no reference |
| A14 | BOM and CRLF catalog bytes with otherwise valid content | Behavior must be explicit; test should verify intended parser handling |
| A15 | Valid quoted CSV description containing comma/quote/newline | Valid parser handles the row without corrupting identity/shape |

## Test batch B — Exact catalog identity lookup

| ID | Synthetic setup | Expected assertion |
|---|---|---|
| B01 | Service kind not exact CATALOG_READY | STOP / OUT_OF_DOMAIN |
| B02 | Expected or observed object invalid type | STOP / DATA_GAP |
| B03 | Unapproved URL/source/status | STOP / KNOWLEDGE_GAP |
| B04 | Missing canonical field in expected or observed | STOP / DATA_GAP; field path listed |
| B05 | Valid traceable HBI snapshot + exact 3-field match | MATCH; all canonical key fields matched |
| B06 | Each canonical field separately differs | MISMATCH; only differing fields listed |
| B07 | Incomplete lineage with equal identity | INCONCLUSIVE / KNOWLEDGE_GAP |
| B08 | Incomplete lineage with differing identity | INCONCLUSIVE; conflict is not definitive |
| B09 | Shade name differs but canonical identity matches | Match behavior follows exact three-field key; descriptive field does not alter identity result |
| B10 | Similar code / whitespace / case variation | No normalization; exact mismatch or missing-data behavior |

## Test batch C — Decision output, idempotency and dependency invalidation

| ID | Synthetic setup | Expected assertion |
|---|---|---|
| C01 | Valid MATCH/MISMATCH result + exact reference metadata | Output envelope created; approval state does not inherit |
| C02 | Invalid service kind / blank reference or output ID | ValueError |
| C03 | Invalid result/reference/identity types | TypeError |
| C04 | Non-tuple provenance/evidence pointers or non-string members | TypeError |
| C05 | Definitive outcome without traceable version or with metadata conflict | ValueError |
| C06 | Repeated same semantic inputs | Stable idempotency key |
| C07 | Change each identity key field, source hash/reference, provenance or evidence pointer | Key changes for semantically keyed fields |
| C08 | Effective known dependency changed | INVALIDATE |
| C09 | Non-effective dependency changed only | PRESERVE |
| C10 | Unknown impact on relevant dependency | UNRESOLVED |
| C11 | Unrelated dependency change | PRESERVE |
| C12 | Shade-name change | Explicitly assert documented idempotency/dependency policy; resolve design question |

## Test batch D — Presentation gate and factual events

| ID | Synthetic setup | Expected assertion |
|---|---|---|
| D01 | Valid traceable MATCH output | Displayable identity match only; message has no safety/result/feasibility claim |
| D02 | Valid traceable MISMATCH output | Displayable identity mismatch only; not usable as service-selection approval |
| D03 | Untraceable or malformed envelope | WITHHOLD_INCONCLUSIVE |
| D04 | INCONCLUSIVE outcome | Withheld |
| D05 | STOP outcome | Withheld |
| D06 | Event kind unknown or actor-kind mismatch | ValueError |
| D07 | OUTPUT_PRESENTED for another output ID | ValueError |
| D08 | OUTPUT_PRESENTED when display gate blocks | ValueError |
| D09 | Naive/invalid timestamp | ValueError |
| D10 | Empty output ID or evidence pointer | ValueError |
| D11 | Client acceptance vs execution consent | Different event kinds; never inferred from one another |

## Test batch E — Intake, current-base, target, history, regional state

| ID | Synthetic setup | Expected assertion |
|---|---|---|
| E01 | Missing required intake field(s) | Needs more information; no definitive advice |
| E02 | Image-only required field | Limited review; uncertain data explicitly identified |
| E03 | Invalid type for expected intake value | Fail closed or explicit validation response; no assumption |
| E04 | Current-base invalid level, bool level, unknown source/confidence | Reject/uncertain; no default |
| E05 | Target incomplete or invalid priority/dimension type | Clarification required; no filling unknowns |
| E06 | History unknown vs none reported vs known but missing entries | Distinct statuses |
| E07 | History entries conflict or malformed | Conflict/invalid status blocks dependent review |
| E08 | Missing standard regions | Needs more information |
| E09 | Image-only/unknown regional source | Limited review; uncertain region flagged |
| E10 | Regional conflict or invalid scope/record | Conflict review / invalid scope / invalid record |
| E11 | Extra patch zone present | Does not replace standard roots/mid-lengths/ends coverage |

## Execution recording template

When H0 is authorized, append:
- repository/head commit SHA;
- exact environment and dependency version;
- exact test command(s);
- test count, passed, failed, skipped, xfailed;
- failures and issue links;
- repeatability confirmation;
- whether each H1 acceptance criterion is PASS / PARTIAL / FAIL.

**No status is pre-filled as PASS.** Static existence of tests is not execution evidence.


---

## Post-H0 execution record — 2026-11-20

**Authorization boundary:** Product Owner authorized isolated H1 validation using synthetic data only. This does not authorize H2, real customer data, customer-facing advice, service execution, push, merge, release, or production deployment.

**Repository baseline:** `3478f65e5ec2f28c0b4f5592c1abf62be31272b7` (HEAD remained unchanged during both runs).

**Environment:**
- Python `3.14.6`
- pytest `9.1.1`

**Exact command:**
```powershell
python -m pytest -q tests/test_hair_catalog_provider.py tests/test_hair_catalog_provider_fail_closed.py tests/test_hair_catalog_numbering.py tests/test_hair_catalog_families.py tests/test_hair_color_owner_rules.py tests/test_hair_color_consultation_inputs.py tests/test_hair_color_current_base.py tests/test_hair_color_target_goal.py tests/test_hair_color_service_history.py tests/test_hair_color_regional_state.py tests/test_hair_domain_slice_7a.py
```

**Results:**

| Run | Result | Failed | Skipped | xfailed | Duration | Exit |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 118 passed | 0 | 0 | 0 | 8.56 s | 0 |
| 2 | 118 passed | 0 | 0 | 0 | 6.01 s | 0 |

Repeatability and worktree-integrity checks passed.

**Two local, uncommitted corrections present during the runs:**
1. `app/domain/hair_catalog_identity_lookup.py`: STOP outcomes are presented as `WITHHOLD_STOP`, with `display_allowed=False` and reason `CATALOG_LOOKUP_STOPPED`.
2. `tests/test_hair_color_regional_state.py`: the patch-zone fixture uses the canonical `patch_or_zone` value instead of `patch`.

The final worktree contained only these two modified paths. They were not pushed or committed; the GitHub branch does not yet contain these runtime/test changes. The two successful runs therefore establish local regression evidence for this exact working tree, not CI evidence for a committed GitHub head.

**Acceptance interpretation:** The 118 passing tests are execution results for the 11 listed files; they do not prove every H1 acceptance criterion. A separate preliminary review mapped 59 criteria as 26 PASS, 19 PARTIAL, 14 NOT TESTED, and 0 FAIL. That mapping remains provisional and requires criterion-by-criterion evidence reconciliation before H1 can be declared accepted.

**Current H1 disposition:** `PARTIAL — TEST SUITE PASSED; ACCEPTANCE NOT CLOSED`.
