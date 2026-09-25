# G-O1 — Unified Seller Workflow Contract & Reality Closure v1.0

Issue: #266
Repository: vahidmaghsoudi2/hbi
Reality baseline: 7740d23db21c804742aebc4533e0e401b8b1a006
Status: DESIGN COMPLETE — IMPLEMENTATION NOT AUTHORIZED

## Scope
CUSTOMER -> CONSULTATION -> NEED/CONTEXT -> RECOMMENDATION -> SELLER/CUSTOMER DECISION -> SALE -> INVENTORY/ACCOUNTING -> FEEDBACK/OUTCOME -> FOLLOW-UP -> OUTCOME ASSESSMENT.
Design only. No Recommendation scoring/eligibility change. No Product/Evidence governance change. No automatic FollowUp. No Accounting V1 expansion. No broad UI.

## Reality audit
- Customer: VERIFIED. Customer and consent exist. Evidence: app/models/customer.py; app/api/routers/customers.py.
- Consultation: PARTIAL. Case is the existing consultation anchor. No Consultation entity. Evidence: app/models/case.py; app/services/case_service.py.
- Need/Context: PARTIAL. Case fields include identified_needs, evidence_gaps, confidence, operator_override, reasoning_status; profile/context services feed recommendation generation. No explicit readiness transition.
- Recommendation: VERIFIED. Case/Product scoped; existing eligibility/evidence contract is authoritative. Evidence: app/models/recommendation.py; app/services/recommendation_service.py.
- Decision: CONFIRMED MISSING as a unified seller/customer boundary. Feedback and SpecialistOverride exist, but no authoritative workflow decision entity.
- Sale: VERIFIED. Admin role is required. Sale validates customer/product/recommendation/stock/FX and creates stock movement. Evidence: app/services/sale_service.py; app/api/routers/sales.py.
- Inventory: VERIFIED. Inventory plus StockMovement are authoritative. Evidence: app/models/inventory.py; app/models/stock_movement.py.
- Accounting: PARTIAL. Existing sale financial snapshot and stock movement fields exist; no separate Accounting service/entity was found at this baseline. Preserve Accounting V1.
- Feedback: VERIFIED. Case/Recommendation scoped; CUSTOMER/SPECIALIST/SYSTEM. Evidence: app/models/feedback.py; app/services/feedback_service.py.
- FollowUp: VERIFIED. SCHEDULED -> COMPLETED/CANCELLED, explicit creation, trace validation. Evidence: app/models/follow_up.py; app/services/follow_up_service.py; app/api/routers/followups.py.
- OutcomeAssessment: PARTIAL. Trace validation exists; API currently forces CUSTOMER provenance; FollowUp is required only when linked. Evidence: app/models/outcome_assessment.py; app/services/outcome_assessment_service.py; app/api/routers/outcome_assessments.py.
- Unified audit: CONFIRMED MISSING. app/core/audit.py is structured logging; ProductMutationLog and EvidenceMutationLog are domain-specific. No persistent unified Case workflow timeline.
- Seller role: CONFIRMED MISSING. Authoritative roles are Admin, Editor, Reviewer/QA, PO. Evidence: app/models/user_role.py; app/core/authorization.py.
- Seller explanation: PARTIAL. Recommendation DTO exposes ranking_reasons, eligibility, evidence_refs, warnings, availability and price, but no seller decision surface.
- Automatic FollowUp handoff: CONFIRMED MISSING by design. Current FollowUp is explicit; no scheduler or automatic creation.

## Role boundary
Seller must become an explicit server-enforced role through PO-authorized implementation. Customer owns personal consultation input and customer response. Seller owns consultation handling, recommendation presentation, decision recording and explicit follow-up handoff. Admin owns financial Sale mutation. Existing specialist/governance roles retain their domain authority. System only orchestrates deterministic transitions and emits audit events.

## Canonical state machine
CUSTOMER_IDENTIFIED -> CONSULTATION_OPEN -> NEED_CONTEXT_READY -> RECOMMENDATION_READY -> DECISION_PENDING.
DECISION_PENDING -> DECISION_REJECTED (terminal for selected recommendation), or DECISION_DEFERRED (open; no sale), or DECISION_ACCEPTED.
DECISION_ACCEPTED -> SALE_PENDING -> SALE_BLOCKED (reason required) OR SALE_RECORDED -> INVENTORY_ACCOUNTING_POSTED -> FEEDBACK_PENDING.
FEEDBACK_PENDING -> FOLLOWUP_NOT_REQUIRED OR FOLLOWUP_SCHEDULED -> FOLLOWUP_COMPLETED -> OUTCOME_ASSESSED.
Existing domain statuses remain authoritative; this is an orchestration state machine.

## Transition contract
| From -> To | Authority | Actor | Preconditions | Stop reason | Audit | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| CUSTOMER_IDENTIFIED -> CONSULTATION_OPEN | Case | Seller/customer | customer exists; consent policy | IDENTITY_REQUIRED / CONSENT_REQUIRED | CONSULTATION_OPENED | capture context |
| CONSULTATION_OPEN -> NEED_CONTEXT_READY | Case + context | Seller | active Case; required context | CONTEXT_INCOMPLETE | NEED_CONTEXT_READY | generate recommendation |
| NEED_CONTEXT_READY -> RECOMMENDATION_READY | Recommendation | System | existing recommendation gates | NO_ELIGIBLE_RECOMMENDATION / EVIDENCE_REQUIRED | RECOMMENDATION_READY | explain/present |
| RECOMMENDATION_READY -> DECISION_PENDING | Workflow Decision | Seller | recommendation presented with trace | PRESENTATION_INCOMPLETE | DECISION_PENDING | obtain decision |
| DECISION_PENDING -> DECISION_ACCEPTED | Workflow Decision | Seller + customer | explicit accept | DECISION_REQUIRED | DECISION_ACCEPTED | existing Sale path |
| DECISION_PENDING -> DECISION_REJECTED | Workflow Decision | Seller + customer | explicit reject | DECISION_REASON_REQUIRED | DECISION_REJECTED | close/next action |
| DECISION_PENDING -> DECISION_DEFERRED | Workflow Decision | Seller + customer | explicit defer | DECISION_REASON_REQUIRED | DECISION_DEFERRED | explicit later action |
| DECISION_ACCEPTED -> SALE_PENDING | Workflow/Sale boundary | Seller -> Admin | accepted decision | DECISION_MISSING | SALE_REQUESTED | Admin executes Sale |
| SALE_PENDING -> SALE_RECORDED | Sale | Admin | existing Sale validation | SALE_VALIDATION_FAILED / STOCK_UNAVAILABLE / FX_REQUIRED / PRODUCT_INACTIVE | SALE_RECORDED | verify result |
| SALE_RECORDED -> INVENTORY_ACCOUNTING_POSTED | Sale + StockMovement | System transaction | sale + stock movement persisted | POSTING_FAILED | INVENTORY_ACCOUNTING_POSTED | await feedback |
| INVENTORY_ACCOUNTING_POSTED -> FEEDBACK_PENDING | Workflow | Seller/system | financial boundary complete | FINANCIAL_STATE_INCOMPLETE | FEEDBACK_PENDING | explicit outcome |
| FEEDBACK_PENDING -> FOLLOWUP_NOT_REQUIRED | Decision/Feedback | Seller + customer | explicit no-follow-up | FOLLOWUP_DECISION_REQUIRED | FOLLOWUP_NOT_REQUIRED | assess when applicable |
| FEEDBACK_PENDING -> FOLLOWUP_SCHEDULED | FollowUp | permitted owner | explicit request; valid trace | TRACE_INVALID / FOLLOWUP_REQUIRED_DATA_MISSING | FOLLOWUP_SCHEDULED | perform follow-up |
| FOLLOWUP_SCHEDULED -> FOLLOWUP_COMPLETED | FollowUp | authorized actor | status=SCHEDULED | FOLLOWUP_STATE_INVALID | FOLLOWUP_COMPLETED | assess outcome |
| FOLLOWUP_COMPLETED -> OUTCOME_ASSESSED | OutcomeAssessment | Seller/customer per role | trace valid; linked FollowUp completed when used | OUTCOME_STATE_INVALID / TRACE_INVALID | OUTCOME_ASSESSED | close/open next case |

## Stop reasons
IDENTITY_REQUIRED, CONSENT_REQUIRED, CONTEXT_INCOMPLETE, NO_ELIGIBLE_RECOMMENDATION, EVIDENCE_REQUIRED, PRESENTATION_INCOMPLETE, DECISION_REQUIRED, DECISION_REASON_REQUIRED, SALE_VALIDATION_FAILED, STOCK_UNAVAILABLE, FX_REQUIRED, PRODUCT_INACTIVE, POSTING_FAILED, FINANCIAL_STATE_INCOMPLETE, TRACE_INVALID, FOLLOWUP_REQUIRED_DATA_MISSING, FOLLOWUP_STATE_INVALID, OUTCOME_STATE_INVALID, ROLE_NOT_AUTHORIZED, CUSTOMER_CASE_MISMATCH.
Every stop includes blocker, reason and next allowed human action. No invented fallback.

## Unified audit contract
Required immutable event fields: event_id, timestamp, correlation_id, case_id, customer_id, workflow_state_before, workflow_state_after, event_type, actor_id, actor_role, target_entity, target_id, result, stop_reason, reason, source_reference.
Existing Product/Evidence audit logs remain authoritative for their domains and are referenced, not replaced.

## Seller-facing decision surface
Customer/consent; workflow/Case state; need/context and blockers; existing Recommendation; human-readable explanation from ranking_reasons, eligibility, evidence_refs, warnings, availability and price; explicit seller/customer decision and reason; Sale result; Inventory/StockMovement result; Feedback/Outcome; FollowUp state/owner/next action; unified Case audit timeline; current stop reason.
No parallel Product, Evidence, Recommendation, Sale, Inventory or Outcome source of truth.

## Seller explanation
Answer: what was recommended, why it matches recorded need/context, supporting evidence refs, eligibility state, warnings/unknowns/conflicts, known availability/price, and pending decision. No new scoring formula. Missing data remains UNKNOWN.

## FollowUp handoff
Expose FOLLOWUP_REQUIRED and next action when appropriate. Do not automatically create, schedule, notify or complete FollowUp in V1.

## Implementation WPs — PO authorization required
WP-1 Seller role and authorization.
WP-2 One authoritative workflow state/decision boundary linked to Case.
WP-3 Persist seller/customer decision with actor, role, reason and Case/Recommendation trace.
WP-4 Guard transitions over existing domain services.
WP-5 Append-only workflow event persistence and Case/correlation query.
WP-6 Minimal seller projection and explanation.
WP-7 Positive and negative tests: context, recommendation, decision, sale/stock/FX, trace, roles, FollowUp terminal state, outcome, audit completeness, no automatic FollowUp.

## Acceptance
Implementation is complete only when role enforcement, deterministic transitions, explicit stop reasons, unchanged Recommendation/Product/Evidence/Accounting contracts, explicit FollowUp, queryable audit timeline, real seller explanation, cross-case/customer rejection, positive/negative tests and PO acceptance are all evidenced.

## Final GAP matrix
Customer VERIFIED; Consultation PARTIAL; Need/Context PARTIAL; Recommendation VERIFIED; Seller role CONFIRMED MISSING; Unified decision CONFIRMED MISSING; Sale VERIFIED; Inventory VERIFIED; Accounting PARTIAL; Feedback VERIFIED; FollowUp VERIFIED; Automatic handoff CONFIRMED MISSING; OutcomeAssessment PARTIAL; Unified audit CONFIRMED MISSING; Seller explanation PARTIAL; Unified state machine CONFIRMED MISSING.

Implementation remains unauthorized. This document closes the design/reality audit only.