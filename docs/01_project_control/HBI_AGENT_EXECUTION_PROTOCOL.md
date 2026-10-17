# HBI — Unified Agent Execution, Evidence & Handoff Protocol

**Status:** Proposed for PO-authorized governance change; becomes the sole active cross-agent execution protocol only after merge to `master`.
**Owner:** Product Owner
**Scope:** All AI agents and contributors; mandatory for HBI work, with Product Intake/G8-specific controls below.
**Canonical status tracker for Product Intake/G8:** [Issue #283](https://github.com/vahidmaghsoudi2/hbi/issues/283).
**Product Intake contract:** [Skin Product Intake Execution Contract v1.1](../product-intake-knowledge-registry/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md).
**Current task status:** Read the current canonical roadmap, evidence ledger and execution log; do not infer status from this protocol.

## 1. Authority and precedence

When records conflict, apply this order:

1. Latest explicit Product Owner decision or authorization.
2. Applicable PO-accepted domain contracts and governance decisions, including P4 and the Skin Product Intake Execution Contract v1.1.
3. This protocol for agent conduct, execution, evidence, verification and handoff.
4. The canonical tracker/roadmap for current task status.
5. Evidence ledger and execution log for criterion-level proof and dated execution evidence.
6. PR text, CI status, chat summaries and agent reports as supporting material only.

This protocol does not rewrite product-domain contracts, grant implementation or merge authority, or authorize scope expansion. A more specific accepted domain contract remains authoritative for its domain.

## 2. Read before acting; no repeated work

Before taking action, inspect the latest relevant GitHub state, the canonical file/work item and prior evidence. GitHub's live repository state is the project source of truth; chat memory and summaries are navigation aids, not proof.

- Preserve completed decisions and results unless new evidence demonstrates a specific defect or regression.
- Do not restart discovery, repeat a completed reduction/review, recreate an equivalent document, or ask the PO to repeat information already present in the repository or conversation evidence.
- If an earlier result is missing from the expected location, search existing records and history first. Do not guess or silently substitute a new task.
- In this project, the previously directed reduction from 92 to 62 items is completed work. Continue from the accepted 62-item result. Do not reintroduce the superseded 92-item inventory in active task briefs, handoffs or AI prompts.
- Handoff packets must contain only current decisions, the accepted current result, relevant evidence, known blockers and the next action. Do not copy superseded material merely to provide historical context.
- This rule governs active working summaries and does not claim that public Git history or cached copies have been erased.

## 3. One owner, one task, one canonical record per purpose

Every work item must identify its owner, scope, completion criteria, dependencies and expected evidence.

- Update the existing authoritative artifact in place whenever possible.
- Do not create parallel protocols, roadmaps, status dashboards or evidence ledgers for the same purpose.
- For Product Intake/G8: Issue #283 is the operational tracker; `PRODUCT_INTAKE_ROADMAP.md` is phase/task status; `G8_ACCEPTANCE_EVIDENCE.md` is criterion-level A1–A9 disposition; `PRODUCT_INTAKE_EXECUTION_LOG.md` records dated sessions and raw evidence.
- A change proposal/PR is a delivery mechanism, not a second source of truth.
- When a document is retired, remove it from the active tree only after its current rules are reconciled into the replacement and inbound active references are updated. Do not leave retired text looking like a live instruction.

## 4. Execution sequence and stop conditions

For each task:

1. Pin the current repository HEAD and relevant branch/PR state.
2. Read the governing instruction and dependencies.
3. State the smallest concrete action and its acceptance condition internally or in the work record.
4. Execute only within the authorized scope.
5. Inspect the actual diff or resulting artifact.
6. Run the relevant tests/checks when applicable.
7. Verify the result against the acceptance condition and record the evidence.
8. Update the canonical tracker/log where status changed.
9. Report the actual state and name the next owner.

Stop and report a precise blocker if authorization, required evidence, access, or a dependency is missing. Do not bypass the blocker, change scope silently, or convert a planned action into a completion claim.

## 5. Evidence and truthful status vocabulary

These states are distinct and must never be conflated:

- **PLANNED:** not executed.
- **DONE:** the owner has made the change or completed the action.
- **VERIFIED:** the result was checked against repository reality and the stated criteria.
- **ACCEPTED:** the PO or designated authority accepted the result.
- **MERGED:** the change is integrated into the target branch.
- **BLOCKED:** a named dependency or control prevents progress.
- **NOT VERIFIED / UNVERIFIABLE:** evidence is insufficient to confirm the claim.

`DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED`.

For every material completion claim, provide the relevant path or URL, branch/commit SHA, and test/run or primary evidence where applicable. Do not claim an edit, comment, commit, test, merge, or cleanup succeeded until the tool/repository confirms it. A CI pass, fixture, screenshot, proposal, or agent statement alone does not prove a real operational workflow.

If a tool rejects or blocks an action, report it as not completed. Do not disguise an attempted action as a successful one.

## 6. Independent verification

The work owner must self-check the result. High-risk changes and claims that affect governance, data integrity, permissions, production data, product lifecycle, evidence readiness or recommendations require an independent verifier other than the sole work owner, unless the PO records an explicit exception.

The verifier must inspect the actual diff/commit and relevant evidence, test acceptance criteria, and issue a verdict: `VERIFIED`, `VERIFIED WITH LIMITATIONS`, `PARTIAL`, `FAILED` or `UNVERIFIABLE`. A review that only repeats the owner's report is not independent verification. Repository reality and reproducible evidence prevail over conflicting claims.

## 7. Authorization, repository safety and irreversible actions

- No direct push or merge to the protected default branch by an agent; use the repository's PR/review process.
- No merge without explicit PO authorization, even if CI is green or a reviewer recommends merging.
- No production DB mutation, migration, schema change, product approval/activation, stock creation, scoring/weight/threshold change, or changes to protected Product A–D without the specific required authorization.
- Do not delete, overwrite, reset, clean, force-push, rewrite merged history, or remove a source of evidence unless the PO explicitly authorizes that exact class of action and the required replacement/reconciliation has been verified.
- Preserve working-tree changes and evidence. Never invent commands run, test output, logs, artifacts or source facts.
- Domain-specific scripts may have their own formatting/usage conventions; those conventions cannot override this protocol's authorization, evidence or truthful-reporting rules.

## 8. Product Intake and G8 controls

- Manufacturer claims are not scientific facts. Preserve provenance and distinguish `FACT`, `MANUFACTURER_CLAIM`, `EVIDENCE`, `INFERENCE`, `UNKNOWN` and `CONFLICT`.
- Empty and UNKNOWN are distinct; neither means safe or eligible.
- Product eligibility, customer eligibility and need matching remain distinct. No keyword-only match, invented relationship, or numeric scoring/weighting is authorized by this protocol.
- AI may research, extract, structure and explain; it cannot independently approve, activate or bypass human/governance gates.
- G8 remains `BLOCKED / NOT VERIFIED` until the A1–A9 ledger is supported by traceable raw operator evidence and the required independent review. CI or browser fixtures are not real-pilot acceptance.
- Do not initialize, seed, delete or mutate an isolated pilot DB until its provenance, isolation boundary and evidence-capture path are verified.

## 9. Correcting a prior mistake

When a prior claim or artifact is found to be wrong:

1. Identify the exact incorrect claim and the authoritative artifact.
2. Preserve the original evidence needed to understand the correction.
3. Correct the existing authoritative artifact through the approved repository path; do not create competing instructions.
4. Update affected links and records so future agents encounter the current rule first.
5. Verify the actual resulting content and state.
6. Explicitly identify any remaining stale reference, public-history limitation or blocked step.

Never hide a failed correction attempt or state that a correction was applied when it was not.

## 10. Retiring and superseding protocol documents

This file is intended to be the sole active **cross-agent execution/evidence/handoff protocol** after merge. Any older protocol that overlaps this scope must be reconciled into this file and removed from the current active tree in the same reviewed change; it must not remain linked or labeled ACTIVE. Specialized domain contracts and script-specific usage guidance remain only for their distinct scope and may not override this protocol.

Deleting a file from the current tree does not erase prior public commits, forks, caches or copies. Do not claim otherwise. Do not rewrite merged Git history as part of routine retirement.

## 11. Communication and handoff format

Keep status messages concise, unified and forwardable. Do not split one operational update across multiple messages or paste long repository files when a stable GitHub path, section and SHA are sufficient.

For a task handoff, use this header when it helps identify the recipient and origin:

```text
FROM:
RECEIVED FROM:
TO:
SUBJECT:
STATUS: FACT | CONTRACT | DESIGN PROPOSAL | OPEN DECISION | UNKNOWN | CONFLICT
CURRENT SHA:
EVIDENCE / PATH:
BLOCKER:
NEXT ACTION:
TURN OWNER:
```

Classify claims accurately: a repository-observed fact is not the same as a PO-approved contract, a proposal, an open decision, an unknown, or a conflict. Never present a proposal as an accepted decision. Leave unavailable fields explicitly unknown rather than filling them with guesses.

## 11. Mandatory handoff format

Every handoff to another agent or a new chat must include only:

- **Current authoritative state:** exact status and source URL/path.
- **Completed and verified:** artifact/commit and evidence.
- **Not done / blocked / unverified:** explicit gaps without euphemism.
- **Binding constraints:** only those needed for the next task.
- **Next action and owner:** one concrete action and who must perform it.

Do not include superseded lists or duplicate historical instructions. Never ask the PO to repeat completed work when it can be recovered from existing records.

---

**Effective-state rule:** Until this file is merged to `master` and the old active references are updated, it is a proposed replacement, not yet the live canonical protocol.