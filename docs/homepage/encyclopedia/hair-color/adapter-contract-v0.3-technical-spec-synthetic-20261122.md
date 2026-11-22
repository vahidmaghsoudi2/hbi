# Adapter Contract 0.3 — synthetic technical specification (implementation-ready draft)

**Date:** 2026-11-22  
**Status:** Technical spec draft for synthetic scope only. It does not authorize runtime/schema/test implementation, product advice, chemical rules, real-client data, pilot, or release.  
**Prior-work rule:** This document refines the existing 0.3 proposal; it does not repeat the H1 audit, ownership matrix, or PO decision record.  
**Inputs:** Adapter 0.2-draft; H1 audit; ownership/publication gates; 0.3 revision proposal; Chat 1 technical decision record.

## 1. Scope of this revision

Only technical envelope and validation behaviors are specified here. All values and evidence refs in test examples must be synthetic placeholders. No real product/color claims, chemistry, or safety/feasibility assertions are permitted.

Resolved defaults delegated for synthetic contract closure:
- Q1: `ANSWER_QUESTION` requires a non-empty `question`; other operations reject the field.
- S06: retain `KNOWLEDGE_GAP`; suppress candidates. Next-owner is encoded as consultation status: `NEEDS_INFORMATION_OR_TEST` when the caller can supply additional evidence/data, or `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` when specialist ownership is required. The distinction must be explicit; no default inference from the reason code alone.
- S08: introduce typed `NO_VALID_OPTION` reason in the next version; engine state `STOP_OR_REFER_WITH_REASON`; no options. It is not synonymous with `OUT_OF_SCOPE` or `KNOWLEDGE_GAP`.

## 2. Operation-specific request rules

| Operation | Required | Allowed extra | Rejected |
|---|---|---|---|
| `EVALUATE_CASE` | common envelope | case/target snapshot, evidence refs, policy ref | question, question_about |
| `REEVALUATE` | common envelope + fresh snapshot identifiers | change-cause refs, dependency refs | question, question_about; resume token |
| `ANSWER_QUESTION` | common envelope + nonblank question | read-only `question_about` suggestion ref/version; resolved bounded context from Orchestrator | decision/consent/workflow mutation fields |

Question envelope:
```json
{
  "question": "Synthetic example question",
  "question_about": {
    "suggestion_ref": "SUG-MOCK-01",
    "suggestion_version": 1
  }
}
```
The Adapter validates shape only. Orchestrator/Ledger validates that suggestion identity/version is current and eligible; the engine receives only bounded read-only context. No response can carry decision or consent mutation.

## 3. Typed value/provenance record (contract-level minimum)

```json
{
  "field_ref": "FIELD-MOCK-01",
  "field_name": "synthetic_field",
  "knowledge_state": "KNOWN",
  "value": "MOCK-VALUE",
  "source_class": "SYNTHETIC_FIXTURE",
  "source_ref": "SOURCE-MOCK-01",
  "case_ref": "CASE-MOCK-01",
  "case_version": 1
}
```

Rules:
- Required identity and state are validated; optional value is present only when state supports a value.
- `UNKNOWN`, `NOT_ASKED`, `MISSING`, and `CONFLICT` never become empty/default values.
- `KNOWN` may carry false, zero, or empty only if the field's own type permits it; empty string is not accepted as a known non-empty text datum.
- `NOT_APPLICABLE` has no value.
- Provenance class and source refs are synthetically validated; real source-class allowlist and specialist review are outside this draft.
- No image-derived hidden-history or chemical inference fields are defined.

## 4. Candidate structure and validation ownership

Illustrative candidate:
```json
{
  "candidate_key": "CAND-MOCK-01",
  "rank": 1,
  "summary": "Synthetic placeholder only",
  "claims": [
    {
      "claim_ref": "CLAIM-MOCK-01",
      "claim_text": "Synthetic assertion only",
      "rule_ref": "RULE-MOCK-01",
      "evidence_refs": ["EVIDENCE-MOCK-01"],
      "support_status": "MOCK_SUPPORTED"
    }
  ],
  "constraint_checks": [
    {"constraint_ref": "CONSTRAINT-MOCK-01", "status": "PASS", "evidence_refs": ["EVIDENCE-MOCK-01"]}
  ],
  "conditions": [],
  "limitations": ["Synthetic fixture only"]
}
```

Validation split:
- Adapter: structural types, uniqueness, max-3, no forbidden keys, non-empty refs, referential presence against request context, blocked-state option suppression.
- Evidence/claim validator: scope applicability and review status. Evidence reference presence alone is not proof of applicability.
- Orchestrator: exact versions, current case/target/workflow/ledger checks, freshness and atomic publication.
- Policy/specialist authority: any substantive product, chemistry, safety, feasibility, or result rule.

Candidate hard constraints:
- Candidate must be withheld if any required check is `FAIL`, `UNKNOWN`, or absent.
- Global blocking state suppresses all candidates.
- Each candidate key unique within run; ranking values unique and contiguous 1..N, N≤3.
- Ranking must be deterministic under input permutation; ties resolved by stable candidate key only after substantive score/criteria tie.
- No padding to three.

## 5. Reason codes and state compatibility additions

Add `NO_VALID_OPTION` as a typed reason code for contract 0.3. It means evaluated constraints leave no candidate valid in the current synthetic run. It does not imply out-of-scope or missing evidence.

Compatibility requirements:
| Engine state | Consultation status | Reason(s) | Options |
|---|---|---|---|
| `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | no blocking reasons | 1–3, all validated |
| `CONDITIONAL_SUGGESTION` | `SYSTEM_REASONED_SUGGESTION` | no global blocker; candidate conditions explicit | 1–3, conditions structured |
| `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | `DATA_GAP`, `CONFLICTING_DATA`, or `KNOWLEDGE_GAP` when caller can resolve | 0 |
| `STOP_OR_REFER_WITH_REASON` | `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | specialist-owned issue, `SAFETY_CONCERN`, or explicit review reason | 0 |
| `STOP_OR_REFER_WITH_REASON` | `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | `SAFETY_CONCERN` | 0 |
| `STOP_OR_REFER_WITH_REASON` | `OUT_OF_V1_SCOPE` | `OUT_OF_SCOPE` only when formal boundary applies | 0 |
| `STOP_OR_REFER_WITH_REASON` | `NEEDS_INFORMATION_OR_TEST` | `NO_VALID_OPTION` with actionable missing/constraint explanation where caller can resolve | 0 |

`ENGINE_FAIL` remains transport/run failure, not a successful consultation response. It must be correlated to run/request and must not expose candidates.

## 6. Version and publication envelope (Orchestrator-facing; not engine authority)

Minimum freshness tuple to check at publication:
`case_ref + case_version + target_ref + target_version + policy_ref/version + evidence refs/versions + workflow_ref/version + ledger snapshot/version`.

Publication protocol draft:
1. Validate response against the immutable request snapshot.
2. Resolve external current versions and ledger/workflow status.
3. If any material dependency differs, mark run `STALE_SUPPRESSED`; publish nothing from this run.
4. Persist validated candidate(s) and assigned suggestion identity in one transaction or equivalent compare-and-swap boundary.
5. Commit audit/correlation record with run status.
6. Display only after commit succeeds.
7. Retry uses same idempotency key for same request; a new evaluation receives a new run identity.
8. Any failure between validation and commit yields no client-visible candidate. No stale fallback is implicit.

This is a service-boundary specification only; persistence/locking protocol must be implemented and separately tested.

## 7. Test exit checklist for the implementation phase

- [ ] operation-specific question required/forbidden validation
- [ ] typed provenance record states and value/state consistency
- [ ] duplicate candidate key and rank rejected
- [ ] rank permutation determinism, stable tie-break
- [ ] candidate claim evidence link present and request-resolved
- [ ] scope/review applicability delegated and blocks invalid claim
- [ ] hard constraint fail/unknown suppresses candidate
- [ ] max three; no padding
- [ ] S06 next-owner variants distinct, options empty
- [ ] S08 `NO_VALID_OPTION`, options empty
- [ ] full state/reason/status compatibility matrix
- [ ] current ledger exact suggestion ref/version check for question/rejection flows
- [ ] target/case dependency invalidation
- [ ] stop event and restart fresh reevaluation, no automatic resume
- [ ] stale publish suppressed on version race
- [ ] idempotent retry; failed persistence never leaks candidate
- [ ] engine exception and malformed response produce no current result
- [ ] forbidden execution/decision/workflow fields recursively rejected

## 8. Decisions not assumed by this spec

- Specialist's actual domain coverage and evidence approval.
- Product claim/rule catalogue or chemistry.
- Production database, deployment, access-control technology, retention, TTL, notifications, revocation/remediation policy.
- Pilot, customer data, or release authorization.

## 9. Next step without rework

The next implementation task is a bounded synthetic contract revision on the existing adapter branch: operation validation + typed `NO_VALID_OPTION` + state matrix and focused tests. The current adapter and fixtures must first be checked for existing behavior; only failing gaps are changed. Existing test coverage is preserved and not duplicated.
