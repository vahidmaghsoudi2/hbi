# Hair Color technical closure — Chat 1 decisions and exit record

**Date:** 2026-11-22  
**Authority:** PO direction to complete the project in five chats. This record applies only to synthetic technical-contract work and does not authorize real-client data, product/chemical claims, chemistry rules, pilot, or release.  
**Status:** Decisions below are defaults delegated for synthetic contract closure; they do not constitute specialist validation.

## Decisions to unblock the synthetic contract

### Q1 — Question request semantics
**Selected:** Q-A. `ANSWER_QUESTION` requires a non-empty `question` string. The field is forbidden/ignored on other operations only according to explicit contract behavior; for the next contract revision, reject it on other operations to avoid ambiguous requests. Existing suggestion questions may include an optional exact suggestion reference/version only as read-only Orchestrator-resolved context. The Adapter must never infer current status or mutate decision/consent.

### Q2 — S06 (KNOWLEDGE_GAP)
**Selected:** Preserve `KNOWLEDGE_GAP` as the distinct reason. Do not disguise it as a missing client datum. For the draft wire mapping, use `STOP_OR_REFER_WITH_REASON` with `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` only when a specialist is the required next owner; otherwise use `NEEDS_MORE_INFORMATION` + `NEEDS_INFORMATION_OR_TEST` with explicit limitations and no candidate. A single universal mapping is not approved: the contract must encode the next-owner distinction. Synthetic test oracle remains unchanged pending versioned contract update.

### Q3 — S08 (no valid or verified alternative)
**Selected:** Do not map this automatically to `OUT_OF_V1_SCOPE` or `KNOWLEDGE_GAP`. Suppress candidates and return `STOP_OR_REFER_WITH_REASON`. The reason must be a typed, explicit no-valid-option/constraint reason in the next contract revision; if the current enum cannot express it, treat that as a contract gap rather than fabricate a reason. Specialist review is not automatically required unless the case is genuinely unresolved and requires that owner.

## Scope authorized for next chats

- Synthetic-only contract/schema/Adapter/test changes and service-boundary design/test preparation.
- Request validation, candidate structure/evidence linkage validation, state compatibility matrix, version/freshness checks at synthetic publish boundaries, and failure suppression.
- Tests use mock/synthetic evidence refs and inert values only.
- No operational product advice, formulas, chemistry, processing instructions, safety claims, real product catalog activation, real customer data, pilot, deployment, or release.
- PO/specialist blockers must remain explicit and cannot be resolved by coding.

## Chat 1 exit criteria

- [x] Current PR state inspected; PR #651 is open, draft, not merged.
- [x] CI run on current head: HBI CI success; HBI Pilot Browser Proof is still running at inspection time.
- [x] Static audit and proposed test work packages reviewed.
- [x] Technical default decisions documented for question semantics and the S06/S08 distinctions.
- [ ] Implement and test the approved synthetic-only contract changes — next chat.
- [ ] Close all remaining synthetic test and service-boundary gaps — Chats 2–4.
- [ ] Final independent audit and blocker-only completion statement — Chat 5.

## Completion definition

Project status may be called **technically complete for the synthetic-only scope** only when the contract/schema/Adapter/tests are aligned, the full relevant test suite and required CI are green on the final PR head, architecture ownership/freshness/failure boundaries are covered by tests or explicitly scoped out, documentation and master navigation agree, and a final audit identifies no untracked technical blocker.

The hair-color consultation product itself remains **not scientifically validated and not pilot/release-ready** until a qualified specialist independently reviews the required evidence/rules and the PO grants the separate approvals.
