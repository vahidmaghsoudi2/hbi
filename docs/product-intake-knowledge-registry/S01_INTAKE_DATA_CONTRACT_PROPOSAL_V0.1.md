# S01 Intake Data Contract — Proposal v0.1

**Date:** 2026-10-20  
**Status:** PROPOSED / NOT APPROVED  
**Scope:** Draft data contract for S01 customer intake. This is not a production schema, diagnostic rule, referral threshold, or product recommendation authorization.

## Purpose

Keep customer-reported experience, operator observation, instrument measurement, scientific interpretation, and operational decision separate. Preserve unknowns explicitly and retain traceable provenance.

## Proposed fields

| Field | Type | Source | Rule |
|---|---|---|---|
| `record_id` | Stable identifier | HBI | Immutable after creation; never derive from answer text. |
| `problem_concept_id` | Reference or unknown | Problem bank | Use an existing concept only; do not auto-create concepts from free text. |
| `question_id` | Versioned identifier | Intake form | Resolve to the exact question and option set shown. |
| `response_value` | Coded value or raw text | Customer | Preserve raw answer separately from interpretation. |
| `response_status` | Enum | Customer/system | `ANSWERED`, `UNKNOWN`, `SKIPPED`, `CONFLICTING`, `NOT_ASKED`. |
| `source_type` | Enum | Recorder | `CUSTOMER_REPORT`, `OPERATOR_OBSERVATION`, `INSTRUMENT_MEASUREMENT`, `EXTERNAL_EVIDENCE`. |
| `observed_at` | Timestamp or unknown | Recorder/device | Record event/measurement time separately from later entry time. |
| `method` | Identifier/text or unknown | Recorder/device/source | Identify observation or measurement method when applicable. |
| `value_unit` | Unit or not applicable | Instrument | Required for numeric measurements; never infer missing units. |
| `evidence_refs` | List of references | Evidence registry | Scientific interpretations must link to traceable sources. Customer reports are not scientific evidence. |
| `interpretation_status` | Enum | Approved rules/reviewer | `NOT_INTERPRETED`, `UNKNOWN`, `REVIEW_REQUIRED`, `ACCEPTED`. P02 defaults to `UNKNOWN` for now. |
| `review_status` | Enum | Designated reviewer | `DRAFT`, `PENDING_REVIEW`, `ACCEPTED`, `REJECTED`; record reviewer role, date, and rationale. |

## Validation rules

1. **Provenance is mandatory.** Customer report, operator observation, and instrument measurement must not be merged into one field.
2. **Raw data and interpretation are separate.** Preserve the original answer; store any mapping to a problem concept separately with its status and provenance.
3. **Unknown states are explicit.** Missing, skipped, uncertain, and conflicting answers are distinct. None may be converted to “no” or an estimated value.
4. **A measurement requires context.** Capture method/device, unit, body/site location, and time. Do not transfer study-specific thresholds to HBI without independent validation and approval.
5. **No automatic classification.** Answers to the draft S01 questions cannot by themselves set P01 or P02 to Accepted. Do not create numeric confidence scores.
6. **Claims and evidence differ.** Customer statements, manufacturer claims, and scientific findings are different source types. A manufacturer claim alone does not establish efficacy.
7. **No operational authorization.** This contract does not authorize product recommendations, treatment decisions, or referrals. Those require separate approved protocols.
8. **Changes are auditable.** Corrections to answers or interpretations should retain author/role, timestamp, previous value, and reason.

## Acceptance checklist before implementation

- [ ] PO and designated medical reviewer decide the proposed P02 definition and its boundary with P01/P05.
- [ ] Proposed questions undergo comprehension testing with intended users; findings are recorded.
- [ ] Allowed values for response status, source type, interpretation status, and review status are centralized.
- [ ] Field ownership and correction responsibility are assigned.
- [ ] Empty, conflicting, corrected, and “prefer not to answer” paths are tested.
- [ ] Any operational threshold has its own evidence, validation, and explicit approval; otherwise it remains inactive.
- [ ] Review confirms no unintended change to the accepted status of P01/P02/P05/P06/P07 and no product recommendation logic has been introduced.

## Open decision

Decide whether P02 remains a scientific concept that cannot be classified in the first intake release, or whether HBI intends to support instrument-based measurement. Until a decision and validation are recorded:

- P02 remains **Identified + Linked / Undetermined**.
- No device threshold is adopted.
- No automatic classification is allowed.
- No acceptance status or product recommendation is changed.

## Sources to preserve in the evidence registry

- DermNet, “Dry skin”: https://dermnetnz.org/topics/dry-skin
- Fluhr et al., 2024, *Epidermal barrier function in dry, flaky and sensitive skin*: https://doi.org/10.1111/jdv.19745
- Instrument-based skin-type study (PubMed PMID 34747517): https://pubmed.ncbi.nlm.nih.gov/34747517/
- Akdeniz et al., systematic review of dietary fluid intake and skin hydration: https://pubmed.ncbi.nlm.nih.gov/29392767/

These sources provide background, not automatic HBI acceptance criteria.
