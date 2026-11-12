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


## 8. Independent option review — safety, client rights, and operational risk

**Review status:** ANALYSIS ONLY — NO OPTION SELECTED; NO PO DECISION CREATED.

This review assesses the trade-offs visible from the current contract. It does not establish legal requirements, clinical policy, a materiality threshold, or implementation behavior.

### A. Displayed suggestion; decision pending

- **A1 — withhold and re-evaluate:** Strongest advantage is a narrow, low-complexity safety boundary: an unsupported suggestion is not reused, and a new evaluation is required before another suggestion. Main weakness is client transparency: a client who has already seen the old suggestion may not know why it is no longer being relied upon.
- **A2 — A1 plus client notice:** Improves transparency and reduces the risk that the client continues to rely on a stale displayed suggestion. It introduces unresolved communication questions: who sends the notice, when it is sent, what wording is accurate, and how delivery is recorded. None is defined in the current contract.
- **A3 — PO alternative:** Any alternative must preserve withholding of unsupported dependent output and must not imply that the prior display remains current.

**Review finding:** A1 is the minimum safety floor already implied by the fixed principles. A2 addresses a separate transparency concern, but its communication mechanics and ownership need an explicit policy. This is a trade-off, not a selection.

### B. Accepted suggestion; no service and no execution consent

- **B1 — historical acceptance plus fresh evaluation and fresh client decision:** Preserves the audit trail and prevents acceptance of the old suggestion from being transferred to a replacement. It avoids confusing acceptance with execution consent. The client still needs a clear explanation that the replacement is a new proposal.
- **B2 — B1 plus explicit notice:** Adds transparency about why the previously accepted suggestion is no longer current. As with A2, notice content, timing, responsibility, and delivery evidence remain undefined.
- **B3 — PO alternative:** Must not treat the old acceptance as evidence validation or as consent to execute.

**Review finding:** The fresh client decision for a replacement suggestion is consistent with the existing separation of suggestion acceptance and execution consent. The unresolved choice is whether explicit notice is an additional mandatory step; no current rule settles it.

### C. Execution consent exists; no service step performed

- **C1 — renewed consent only if the suggestion or material service basis changes:** Avoids unnecessary repeated consent when a fresh evaluation genuinely leaves the service proposal unchanged. However, it depends on a reliable decision about what counts as a material change. The contract has no approved materiality threshold, decision owner, or method. Without those, C1 is not sufficiently determinate to become a test oracle or executable rule.
- **C2 — renewed consent in every case:** Is easier to state and avoids relying on an undefined materiality judgment. It provides a clear opportunity for the client to reconsider after the evidence revision. Its cost is additional consent friction, including cases where the fresh evaluation does not change the proposal.
- **C3 — PO alternative:** Must preserve the rule that prior consent is historical and cannot validate changed evidence. No affected service step should proceed while its supporting evaluation is unresolved.

**Review finding:** Both C1 and C2 can be expressed without erasing the original consent event, but C1 requires a materiality policy first. C2 is more conservative about client re-authorization but is not automatically approved by that fact. The current contract does not select between them.

### D. One or more service steps performed

- **D1 — hold affected future steps; specialist review and fresh evaluation; separate remediation policy:** Keeps the response scoped to steps whose support may have changed and avoids inventing rollback or compensation. Its critical dependency is reliable identification of affected versus independent remaining steps. If that dependency cannot be established, the contract's existing fail-closed principle does not permit assuming that a step is unaffected.
- **D2 — broader stop-and-escalate with client notice:** Makes escalation and client communication more explicit and may be easier to govern when the impact is uncertain or spans several steps. Its risk is over-broad interruption of steps that may be independent, and it still needs a named accountable owner and separately approved remediation/customer-care rules.
- **D3 — PO alternative:** Must preserve the record of performed work, must not imply automatic rollback, and must not infer permission to continue remaining work from the fact that earlier steps occurred.

**Review finding:** D1 and D2 address different scopes of containment. D1 depends on dependable dependency knowledge; D2 avoids relying on narrow dependency classification but may stop more of the case than necessary. The current evidence does not justify selecting one globally. Where dependency impact is unknown, the existing fail-closed boundary remains the minimum constraint; the exact scope and escalation owner require PO/specialist policy.

### Cross-scenario control gaps to resolve before any test oracle

1. **Materiality authority:** Identify who determines whether an evidence revision is material and what evidence that determination relies on. Do not create a numeric or categorical threshold by inference.
2. **Communication responsibility:** Decide whether notice is required in A, B, C, and D separately; identify the accountable sender and the approved communication policy before defining delivery mechanics.
3. **Decision separation:** Record acceptance and execution consent as distinct historical decisions. A fresh acceptance decision must not be treated as renewed execution consent.
4. **Remaining work:** For C and D, define which authority can hold or release a future service step. A prior consent or completed earlier step does not itself authorize continuation after a material evidence change.
5. **Performed work:** Keep performed steps factual and historical. Remediation, compensation, rollback, and customer-care handling require separate approved policies; they cannot be inferred from this proposal.
6. **Uncertain dependency:** Do not label an output or step independent merely because its dependency is undocumented or unknown.

### Review disposition

- A1–D3 remain unselected.
- The safety floor remains: do not present or act on dependent suggestions as currently supported when their material evidence is no longer applicable; preserve historical client decisions; do not infer acceptance, consent, or continuation permission.
- The remaining choices are policy decisions for the Product Owner, informed by the already approved specialist role where the matter is technical/safety-related.
- No fixture, schema, runner, test oracle, runtime behavior, PO register decision, or implementation authorization is created by this review.
