# Mandatory Staged Execution Protocol — Skin Product Intake (G8 Pilot)

**Authority:** Product Owner (PO)  
**Governing mission:** [Issue #283 — HBI Product Intake → G8 Real Product Pilot](https://github.com/vahidmaghsoudi2/hbi/issues/283)  
**Binding contract:** [Skin Product Intake Execution Contract v1.1](../architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md)  
**Progress roadmap:** [Product Intake Roadmap](../product-intake/PRODUCT_INTAKE_ROADMAP.md)  
**Acceptance evidence ledger:** [G8 A1–A9 Evidence Ledger](../product-intake/G8_ACCEPTANCE_EVIDENCE.md)  
**Execution log:** [Product Intake Execution Log](../product-intake/PRODUCT_INTAKE_EXECUTION_LOG.md)  
**Created:** 2026-10-14  
**Purpose:** Prevent lost decisions, duplicate work, unsupported completion claims, and conflicting project status across agents and chat sessions.

## 1. Authority and source-of-truth order

Every agent working on Product Intake must read this protocol, the binding contract, the current progress roadmap, the A1–A9 evidence ledger, and the relevant part of Issue #283 before proposing or performing project work.

When records disagree, do not silently choose one or create a parallel status record. Reconcile the discrepancy against this order:

1. Explicit, latest Product Owner decision or authorization.
2. Approved binding contract and applicable governance decisions.
3. This execution-control protocol.
4. The canonical Product Intake roadmap for phase and task status.
5. The A1–A9 ledger and execution log for evidence and runtime dispositions.
6. PR descriptions, CI results, chat summaries, and agent-generated reports as supporting material only.

A CI pass, merged documentation, test fixture, or agent assertion does not by itself prove real-pilot acceptance.

## 2. One canonical progress record

This protocol defines **how work is controlled**. It does not create a second copy of phase checkboxes, current phase status, or A1–A9 dispositions.

- Record phase/task status in `docs/product-intake/PRODUCT_INTAKE_ROADMAP.md`.
- Record criterion-level proof and PASS / FAIL / NOT VERIFIED in `docs/product-intake/G8_ACCEPTANCE_EVIDENCE.md`.
- Record dated operator sessions, exact environment, raw artifacts, and readbacks in `docs/product-intake/PRODUCT_INTAKE_EXECUTION_LOG.md`.
- Use Issue #283 as the governing operational tracker.
- This file is the mandatory execution-control rule, not a substitute for those records.

If the canonical roadmap and another record disagree, log the mismatch and correct the canonical record through the repository's normal review process. Do not create another roadmap to work around the mismatch.

## 3. Execute only the first actionable unchecked item

Before acting, identify the first unchecked item in the canonical roadmap and confirm its dependencies.

- Work only on that first **actionable** unchecked item; do not skip ahead to a later item for convenience.
- If the item is blocked by a PO decision, authorization, independent review, missing artifact, or technical dependency, record the exact blocker and stop. Do not mark it complete or silently bypass it.
- If the roadmap's ordering or dependency is demonstrably inconsistent, report the conflict and propose a documented correction; do not reorder the work unilaterally.
- Keep unrelated sales, purchasing, Home Page, or other work out of this mission unless a verified dependency directly affects Product Intake.

## 4. Completion and evidence rule

An item may be checked complete only after its stated acceptance conditions are met and the supporting evidence is available.

For every completion claim, record as applicable:

- exact repository path and relevant symbol, test, endpoint, or UI action;
- exact commit SHA and branch;
- test/workflow run URL and result, where applicable;
- raw request/response, runtime log, persisted readback, or other primary artifact;
- timestamp, environment/session identifier, and operator role for runtime work;
- independent reviewer and disposition where the roadmap or acceptance criterion requires it.

Use `Path + Symbol + SHA` where applicable, but do not invent a symbol for documentation-only or operational work. Link the actual artifact instead. Summaries without the underlying evidence are not sufficient to mark an acceptance criterion PASS.

Update the canonical roadmap and execution log in the same coherent change as the work, or in the next explicitly linked documentation change when the evidence cannot be committed with the implementation. Record the commit SHA and date. Never claim a repository update succeeded until GitHub confirms the write or merge.

## 5. Locked phases and completed items

A checked item is treated as **LOCKED against routine repetition**. Agents must not redo it, reopen old discussions, or recreate equivalent documents merely because a new chat starts.

A lock does not authorize ignoring credible evidence of a defect, regression, security issue, data-integrity risk, or incorrect completion claim. In that case:

1. Preserve the existing completion record.
2. Record the new evidence and explain why it challenges the prior result.
3. Notify the PO and propose the narrowest corrective action.
4. Reopen or change a locked item only with explicit PO authorization, except that urgent containment of a credible safety/security/data-integrity risk must be raised immediately and must not be concealed by the lock.

Use the PO command `!LOCK PHASE X` to explicitly lock a phase. Reopening a PO-locked phase requires `!OVERRIDE_LOCK PHASE X`. These commands are governance instructions, not technical access controls; repository permissions, reviews, and branch protections remain necessary.

## 6. Authorization and safety boundaries

This protocol grants no implementation, merge, production, or product-activation authority beyond existing explicit authorization.

Unless the PO separately authorizes otherwise, agents must not:

- access or mutate production data for the pilot;
- run migrations or make unapproved schema changes;
- change Product A–D;
- receive or fabricate stock;
- change recommendation scoring, weights, thresholds, or EvidenceReadiness semantics;
- infer `product_line=SKIN` instead of requiring explicit selection;
- convert manufacturer claims, inferences, unknowns, or conflicts into verified facts without the contract's evidence and review gates;
- approve, activate, or make a product recommendation-ready by bypassing required gates;
- merge a PR without explicit PO authorization.

Registration of this protocol or a green CI result is not authorization to merge other PRs or to declare G8 accepted.

## 7. G8 acceptance rule

G8 remains `BLOCKED / NOT VERIFIED` until all required A1–A9 criteria have evidence that is raw, traceable to the exact code and environment, and independently reviewed according to the canonical ledger.

- `DONE` is not the same as `VERIFIED`.
- `VERIFIED` is not the same as `ACCEPTED`.
- `ACCEPTED` is not the same as `MERGED`.
- No criterion may be marked PASS solely because a test suite or CI workflow passed.
- No real-pilot success, cleanup, or production isolation may be claimed without the corresponding primary evidence.

## 8. Progress-log discipline

After each material action, add a concise entry to the canonical execution log and update the canonical roadmap if task status changed. Each entry must state:

- date/time;
- item or acceptance criterion affected;
- action taken and outcome;
- evidence links and exact SHA;
- remaining blocker or next authorized action.

Do not add a completion checkmark for work that is merely planned, under review, waiting for authorization, or supported only by an unverified report.

## 9. End-of-turn handoff

Every agent handoff must end with these three points:

1. **Current position:** phase/task and exact status, taken from the canonical roadmap.
2. **Evidence and blockers:** links/SHA for completed work and explicit missing proof or pending decision.
3. **Turn owner:** who must act next (agent, independent reviewer, or PO).

Do not ask the PO to repeat information or rerun a test when the existing repository record or previously supplied raw output already contains it. First retrieve and assess the existing evidence.

## 10. Completion of the roadmap

When all canonical roadmap items are complete, verify that each has evidence and that the A1–A9 ledger has independent dispositions. Then report:

> "The roadmap is complete. G8 acceptance is stated separately according to the A1–A9 evidence ledger. Awaiting the PO's next instruction."

Never state that G8 is complete merely because all administrative roadmap checkboxes are checked.

---

**Governance intent:** This protocol prevents duplicate work and status drift while preserving evidence-based correction, PO authority, and the existing binding Product Intake contract.

## 11. PO-approved correction, single source, and minimum-document rule

This rule is mandatory for every agent working on HBI Product Intake.

1. **Identify before acting.** When an error or contradiction is suspected, locate the authoritative file or work item and gather the evidence. Do not guess from a chat summary or create another record to work around uncertainty.
2. **Propose and obtain PO approval.** Before changing or removing anything, state the evidence, the exact correction, the existing artifact to change, the expected impact, and any unavoidable repository constraint. Wait for the PO's explicit approval. Do not create branches, PRs, documents, or close work items before that approval.
3. **Correct the existing authoritative artifact.** After approval, replace the incorrect content in its current authoritative file or work item. Do not create a second policy, roadmap, status ledger, or equivalent document. Keep the number of authoritative documents to the minimum required by the existing architecture.
4. **Respect repository controls without multiplying records.** If the protected default branch rejects direct edits, use the repository-required review path to change the existing file only. Such a PR is a delivery mechanism for that one correction, not a new source of truth. Do not open parallel PRs for the same correction. Reuse an existing suitable, unmerged PR only if its purpose and scope can be changed without preserving unrelated or misleading work; otherwise explain the constraint and obtain PO approval before opening a replacement.
5. **Remove superseded active paths.** Once the approved replacement is in place, close or remove duplicate, unmerged work as explicitly directed by the PO. Do not leave obsolete drafts presented as active instructions. Preserve the repository's historical audit trail; do not rewrite merged Git history.
6. **Verify and report state.** Confirm the exact file, branch, commit, PR state, and whether the correction is merged. Clearly separate DONE, NOT DONE, BLOCKED, and awaiting PO action. Never report a proposed or unmerged correction as applied to the default branch.
7. **No routine repetition.** Before starting work, inspect the current authoritative record and prior evidence. Do not repeat completed work or ask the PO to repeat a check when existing evidence is available, unless a specific gap or regression is demonstrated.

**Default principle:** one authoritative document per purpose, one approved correction path per defect, no duplicate source of truth, and no execution before PO approval.

