# S01 PO / Medical Review Packet — V0.1

**Status:** REVIEW PACKET / NOT APPROVED  
**Scope:** S01 preliminary skin-problem intake; decision support for Product Owner (PO) and qualified medical reviewer.  
**Parent work:** PR #416 — preliminary S01 evidence review.  
**Rule:** This packet organizes decisions; it does not make clinical decisions on behalf of the PO or medical reviewer.

## 1. Decisions that can proceed without clinical sign-off

These are documentation and governance defaults, not clinical acceptance:

| ID | Proposed default | Required record |
|---|---|---|
| R01 | Keep customer report, operator observation, instrument measurement, scientific interpretation, and operational decision as separate data layers. | Field/source mapping and reviewer rationale |
| R02 | Preserve unknown, skipped, not asked, conflicting, and unavailable as distinct states; never silently convert them to negative answers. | Status vocabulary and examples |
| R03 | Keep evidence provenance with each substantive claim: source, source type, access/reference, relevant passage or finding, limitations, and review state. | Evidence record |
| R04 | Treat the proposed data contract and Q1–Q6 as drafts only; do not deploy them or alter production schema under this PR. | Explicit approval gate before implementation |
| R05 | Keep skin-problem intake, product entry/product knowledge, and the later problem-to-product relationship layer as separate workstreams with explicit interfaces. | Interface decision record |
| R06 | Do not use numeric confidence, automatic classification, ingredient overlap alone, product ranking, or recommendation behavior as a substitute for evidence and review. | Acceptance checklist |

**Disposition:** These defaults can be retained as process/documentation rules. They do not change accepted problem statuses.

## 2. Decisions requiring explicit PO and/or medical review

### D01 — P01 and P02 conceptual boundary
**Question:** Should dry skin/xerosis (P01) and reduced stratum-corneum hydration/dehydration concept (P02) remain distinct, related concepts rather than being merged?  
**Proposed default:** Keep separate and linked, with P02 still "Identified + Linked / Undetermined".  
**Approver:** PO; medical reviewer confirms clinical wording.  
**Evidence to record:** Decision, rationale, any terminology changes, reviewer and date.  
**Gate:** Must not change current statuses without recorded approval.

### D02 — Can customer answers alone classify P02?
**Question:** May the initial intake infer/classify P02 from customer-reported sensations or answers alone?  
**Proposed default:** No. Capture reports as reports; leave interpretation undetermined unless a separately approved method supports it.  
**Approver:** PO + medical reviewer.  
**Evidence to record:** Yes/no decision, permitted interpretation, limitations, validation basis.  
**Gate:** No classification rule until approved and validated.

### D03 — Instrument measurements in the initial release
**Question:** Will the initial S01 workflow support instrument-based measurements, or remain report/observation-only?  
**Proposed default:** Do not require or operationalize instrument measurements in the initial intake until a method, units, device, quality controls, and interpretation limits are specified.  
**Approver:** PO + medical reviewer; device/method owner if applicable.  
**Evidence to record:** Scope choice, named method/device if included, units, conditions, quality controls, limitations, and validation plan.  
**Gate:** Never transfer study-specific thresholds directly into HBI.

### D04 — Are Q1–Q6 suitable for customer-facing use?
**Question:** Approve, revise, or reject the draft questions in the working record?  
**Proposed default:** Keep them as review-only drafts; do not deploy.  
**Approver:** PO + medical reviewer; usability review where needed.  
**Evidence to record:** Each question's decision, final wording, response options, purpose, risk of ambiguity, and version/date.  
**Gate:** No real-world use until the complete question set and response handling are approved.

### D05 — Operational interpretation and safety/referral protocol
**Question:** What, if any, findings require stopping routine intake or escalating to a qualified professional?  
**Proposed default:** Do not invent thresholds or referral triggers in this documentation task. Use an already approved organizational safety protocol if one exists; otherwise keep this gate open.  
**Approver:** Qualified medical reviewer and PO.  
**Evidence to record:** Authoritative protocol/source, exact approved triggers, action owner, exception handling, and version/date.  
**Gate:** No new clinical threshold or referral rule until explicitly approved.

### D06 — Accepting problem-to-product relationships
**Question:** What relationship types may eventually connect a skin-problem concept to a product or product claim, and what evidence is required for each?  
**Proposed default:** Design the relationship record separately; do not create accepted links or infer suitability from ingredient overlap, shared words, or manufacturer claims alone.  
**Approver:** PO + medical/evidence reviewer; product-knowledge owner for product-claim provenance.  
**Evidence to record:** Relationship type and direction, applicability, supporting evidence and evidence kind, limitations/contraindications, review status, reviewer/date/rationale, validity state.  
**Gate:** Relationship model and individual relationships require separate approval. This gate does not authorize recommendations.

### D07 — May a relationship trigger a recommendation?
**Question:** Can any accepted relationship affect product display, selection, or recommendation behavior?  
**Proposed default:** No recommendation or ranking behavior is authorized by this PR. Treat future relationship data as reviewed knowledge until a separate explicit behavior specification and validation are approved.  
**Approver:** PO; medical reviewer for any clinical implication.  
**Evidence to record:** Permitted behavior, prohibited behavior, rationale, validation cases, and release approval.  
**Gate:** Separate product behavior approval required.

### D08 — Handling conflicting information
**Question:** How should the workflow behave when customer report, operator observation, or measurement disagree?  
**Proposed default:** Preserve each source independently, flag the discrepancy, and leave interpretation unresolved rather than silently selecting one source.  
**Approver:** PO + medical reviewer for any clinical resolution protocol.  
**Evidence to record:** Conflict states, who may review, permitted resolution actions, and audit trail.  
**Gate:** No automated conflict resolution.

## 3. Minimal decision response template

For each D01–D08, record only:

- **Decision:** Approve / Revise / Reject / Defer
- **Decision owner(s):**
- **Rationale:**
- **Evidence/source relied upon:**
- **Scope and limitations:**
- **Follow-up action and owner:**
- **Decision date / version:**

A deferred decision remains UNKNOWN or UNDETERMINED as applicable. Silence is not approval.

## 4. Work that may continue in parallel

1. Improve source traceability and distinguish evidence type, finding, limitation, and claim origin.
2. Prepare non-production test cases for unknown/skipped/conflicting responses and provenance completeness.
3. Refine the proposed field contract as a proposal, without schema migration or production writes.
4. Keep the three workstreams separated while documenting the future interface between them.
5. Audit wording for accidental diagnosis, implied product suitability, unsupported thresholds, or status promotion.

## 5. Acceptance gates for this packet

- [ ] PO confirms the proposed process/documentation defaults R01–R06 or records amendments.
- [ ] D01–D08 each has a decision owner and explicit status; unresolved items remain open.
- [ ] Medical review is recorded for clinical terminology, classification, questions, measurements, safety/referral, and clinically meaningful product relationships.
- [ ] Every accepted decision has rationale, evidence/source, reviewer, date, and scope.
- [ ] No draft question or field is represented as approved for production.
- [ ] No problem status, product relationship, recommendation, treatment authorization, or referral threshold changes without its separate approval.
- [ ] Technical CI/browser results are not presented as clinical validation.

## 6. Explicit non-goals

This packet does not diagnose, establish a medical protocol, validate a measurement device, approve customer-facing questions, modify production schema, accept a problem-to-product link, enable recommendation behavior, or authorize merging PR #416.

## 7. Current baseline preserved

- P01 dry skin/xerosis: Scoped / Deferred.
- P02 dehydration/impaired moisture-retention concept: Identified + Linked / Undetermined; separate from P01.
- P05 sensitive skin remains separate from P01.
- P06 irritant dermatitis remains a clinical anchor, not an accepted operational problem.
- P07 fissuring remains separate; no safety threshold is inferred.

Any change to these states requires an explicit recorded decision in the appropriate canonical record.
