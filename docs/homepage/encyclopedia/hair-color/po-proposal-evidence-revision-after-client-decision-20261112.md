# PO Decision Proposal — Evidence Revision After Client Decision

**Status:** DRAFT FOR PO REVIEW — NOT APPROVED  
**Date:** 2026-11-12  
**Scope:** Hair-color consultation only; documentation and policy analysis  
**Branch:** `docs/hair-color-independent-consultation-20261112`

## 1. Purpose

This proposal isolates a policy gap: how a material change in evidence validity should affect a suggestion and client decision that already exists in the case history.

It does not change the approved evidence statuses, engine states, consultation response states, workflow states, or the existing fail-closed publication boundary. It does not define runtime behavior.

## 2. Fixed principles (not reopened by this proposal)

1. Evidence status is scoped to the claim and its applicable subject, product, market, version, and conditions. A change must not be applied indiscriminately to every claim in a document or every suggestion in a case.
2. A suggestion dependent on evidence that is no longer applicable must not be represented as currently supported for a future publication or service step.
3. Historical client events must remain auditable and must not be silently erased or rewritten.
4. Acceptance is not execution consent; execution consent is a separate client decision.
5. A client decision cannot make invalid, conflicting, unverified, not-applicable, or outdated evidence authoritative.
6. Evidence availability cannot create client consent.
7. Unknown dependency impact is not proof of independence. If material dependency cannot be resolved, dependent output is withheld under the existing fail-closed boundary.
8. No automatic expiry, TTL, revocation, notification, reconfirmation, rollback, or remediation policy is currently approved.

## 3. Four situations requiring an explicit PO policy

### A. Suggestion displayed; client decision is still pending

**Known boundary:** If material evidence becomes inapplicable before a later publication or service step, the dependent suggestion must not be treated as currently supported. The old display remains historical.

**PO question:** Should the client-facing case be explicitly marked as requiring a refreshed assessment, or is withholding the dependent suggestion from subsequent use sufficient?

**Options for review:**
- A1. Withhold the affected suggestion from further use and require a fresh evaluation before another suggestion is presented.
- A2. A1 plus a client-facing notice that the previous suggestion is no longer current.
- A3. Other policy specified by the PO.

### B. Suggestion accepted; service has not started; no execution consent exists

**Known boundary:** Acceptance remains a historical event and is not execution consent. The acceptance event cannot validate changed evidence.

**PO questions:**
- Does the prior acceptance remain recorded only as historical, with the suggestion requiring fresh evaluation?
- Is explicit client notice required before presenting a replacement suggestion?
- Must the client make a fresh acceptance decision after the new evaluation?

**Options for review:**
- B1. Preserve prior acceptance as historical; require fresh evaluation and a fresh client decision for any replacement suggestion.
- B2. B1 plus explicit client notice of the material evidence revision.
- B3. Other policy specified by the PO.

### C. Execution consent exists; no service step has been performed

**Known boundary:** Consent is a historical event, not evidence validation. The current contract does not establish whether that consent remains usable after a material evidence revision.

**PO questions:**
- Must the affected service step be held pending fresh evaluation?
- Is renewed explicit consent required if the evaluated suggestion or material basis changes?
- If fresh evaluation finds no material change to the suggestion, may prior consent remain applicable, or is renewed consent still required?

**Options for review:**
- C1. Hold the affected service step; require fresh evaluation; require renewed explicit consent only if the suggestion or material service basis changes.
- C2. Hold the affected service step; require fresh evaluation and renewed explicit consent in all cases.
- C3. Other policy specified by the PO.

### D. One or more service steps have already been performed

**Known boundary:** Historical performed steps must remain recorded. The current contract does not define clinical/technical remediation, client notification, compensation, rollback, or how to handle remaining steps.

**PO questions:**
- Who is accountable for deciding whether remaining steps can proceed?
- Is specialist review mandatory when the evidence revision is material to the remaining service?
- What client-notification and escalation policy applies?
- Which separate operational, safety, legal, or customer-care policy governs work already performed?

**Options for review:**
- D1. Do not infer continuation permission. Hold only affected future steps pending specialist review and fresh evaluation; preserve the performed-step record. Refer remediation and customer-care actions to separately approved policies.
- D2. Define a broader stop-and-escalate policy for the whole case, including client notice, through a separate specialist/operational review.
- D3. Other policy specified by the PO.

## 4. Cross-cutting decision questions

The PO should decide, separately for each situation above:

1. Whether client notification is mandatory, optional, or governed by a separately approved communication policy.
2. Whether fresh acceptance is required after re-evaluation.
3. Whether renewed execution consent is required, and under what material-change threshold.
4. Who is accountable for deciding whether a change is material: evidence authority, specialist, operational owner, or a defined combination.
5. For partly performed service, who owns the decision on remaining steps and which separate policy governs remediation.

These questions must not be collapsed into a single automatic revocation rule.

## 5. Recommended decision-record format

For each of A–D, record:
- selected option or a PO-authored alternative;
- accountable decision owner;
- whether notification is required;
- whether fresh acceptance is required;
- whether renewed execution consent is required;
- treatment of remaining unperformed steps;
- separate policy owner for any remediation of performed steps.

A decision for one situation must not be silently generalized to the other three.

## 6. Explicit non-decisions and exclusions

This proposal does **not**:
- approve any of options A1–D3;
- define a materiality threshold or status-transition precedence;
- define event ordering, atomic compare-and-publish, ledger fields, dependency graph, identifiers, or runtime schema;
- define automatic revocation, suspension, notification, reconfirmation, rollback, compensation, or remediation;
- add a workflow, engine, or consultation response state;
- change fixtures, JSON Schema, runner, tests, product behavior, scientific evidence status, customer data, or the 88-color catalogue;
- authorize implementation, pilot, release, or merge.

## 7. Required next review

PO review is required for the four situations independently. Any selected policy that changes client-facing obligations or service authorization must be recorded as an explicit PO decision before it is translated into contract requirements or synthetic test oracles.

**Current disposition:** OPEN — awaiting PO decision.  
**No approval is implied by placing this proposal in PR #535.**
