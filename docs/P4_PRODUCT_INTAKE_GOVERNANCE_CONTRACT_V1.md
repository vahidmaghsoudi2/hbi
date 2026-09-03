# HBI — P4 Product Intake & Governance Contract

**Contract ID:** HBI-P4-CONTRACT-001  
**Version:** V1.0  
**Status:** PO APPROVED  
**Repository:** vahidmaghsoudi2/hbi  
**Branch:** master  

---

## 1. Purpose

This contract defines the Product Intake, Governance, QA, Evidence, Approval, Activation, Audit Trail, History, and Permission requirements for HBI Product Management.

The contract establishes controlled product lifecycle management and prevents uncontrolled mutation of product governance fields.

---

## 2. Scope

This contract covers:

- Product editing
- Product lifecycle
- Product submission
- QA review
- Evidence readiness
- Product approval
- Product activation
- Identity verification
- Product rejection
- Audit trail
- Product history
- Evidence API governance
- Permission enforcement

This contract does not authorize implementation of P3 functionality that has not been formally accepted.

---

## 3. Roles

### 3.1 Editor

May edit permitted informational Product fields.

### 3.2 Reviewer / QA

May perform QA review and modify QA-controlled fields.

### 3.3 PO

Product Owner with authority over final lifecycle decisions, approval, rejection, and governance exceptions.

### 3.4 Admin

Technical/system administration role. Administrative access must not automatically imply Product governance authority.

Authentication and Authorization are separate requirements.

---

## 4. Product Edit Policy

Editors may modify permitted informational fields.

Reviewer / QA may modify QA-controlled fields.

PO controls final lifecycle decisions.

The following fields are immutable through generic Product PATCH:

- product_id
- historical records

The following governance fields MUST NOT be changed through unrestricted generic PATCH:

- status
- identity_status
- qa_verdict

These fields may only change through controlled workflow transitions.

---

## 5. Product Lifecycle

The mandatory V1 lifecycle is:

DRAFT → SUBMITTED → QA_REVIEW → APPROVED → ACTIVE

Rejection:

QA_REVIEW → REJECTED

Archive:

ACTIVE → ARCHIVED

Invalid lifecycle transitions MUST be rejected.

A generic field update MUST NOT bypass lifecycle controls.

---

## 6. Submit

A Product may be submitted only through the controlled Submit workflow.

Submit changes lifecycle state:

DRAFT → SUBMITTED

The system MUST record:

- actor
- timestamp
- action
- target Product
- previous state
- new state

---

## 7. QA Review

A submitted Product enters:

SUBMITTED → QA_REVIEW

QA review MUST evaluate applicable Product identity, Evidence, conflicts, and quality requirements.

QA approval is distinct from Evidence approval.

Evidence QA status MUST NOT automatically imply Product QA approval.

---

## 8. Evidence Readiness

Before Product approval, the system MUST establish Evidence readiness.

Blocking conditions include:

- missing required Evidence
- unacceptable Evidence status
- unresolved blocking conflicts
- required Evidence QA not completed

Evidence readiness MUST be traceable to the Product approval decision.

---

## 9. Product Approval

Product approval is a controlled PO decision.

The Product MUST NOT become ACTIVE unless the required prerequisites are satisfied.

Minimum prerequisites:

1. Identity requirement completed where applicable
2. Required Evidence acceptable
3. No unresolved blocking conflict
4. Product QA approved
5. PO approval recorded

Approval changes lifecycle state:

QA_REVIEW → APPROVED

---

## 10. Product Activation

Activation is controlled and MUST NOT be performed by generic Product PATCH.

A Product may become:

APPROVED → ACTIVE

only when all mandatory activation prerequisites have passed.

Activation MUST be auditable.

---

## 11. Identity Verification

Identity verification is a separate controlled workflow.

Where required, the system MUST record:

- verification result
- actor
- timestamp
- source/reference
- relevant Product identity information

Identity verification status MUST be governed by controlled transitions.

Identity requirements MUST be satisfied before activation where applicable.

---

## 12. Reject

A Product may be rejected during QA review.

Transition:

QA_REVIEW → REJECTED

Rejection MUST record:

- actor
- timestamp
- reason
- previous state
- new state

A rejection reason is mandatory.

---

## 13. Audit Trail

HBI MUST maintain a true Product Mutation Audit Trail.

The following actions MUST be auditable:

- CREATE
- EDIT
- SUBMIT
- QA_CHANGE
- APPROVE
- REJECT
- ARCHIVE
- IDENTITY_CHANGE
- ACTIVATION

Each audit record MUST contain, where applicable:

- actor
- timestamp
- action
- target
- before state/value
- after state/value or diff
- reason

The audit trail MUST be append-only.

Security logging alone does not satisfy this requirement.

---

## 14. Product History

HBI V1 requires immutable Product mutation history.

History MUST be sufficient to reconstruct:

- who changed what
- when it changed
- previous value
- new value
- reason where applicable

Complex version-control functionality is not required for V1.

---

## 15. Evidence API Governance

Evidence operations required by the Product governance workflow MUST be available through controlled API operations.

Evidence changes affecting:

- QA
- approval
- activation
- conflict resolution

MUST be auditable.

Physical deletion MUST NOT destroy required traceability.

Where appropriate, Evidence should be rejected, invalidated, or superseded rather than silently deleted.

---

## 16. Permission Enforcement

| Action | Editor | Reviewer / QA | PO | Admin |
|---|---|---|---|---|
| Edit informational Product fields | YES | YES | YES | Technical |
| Change QA-controlled fields | NO | YES | YES | Technical |
| Submit Product | NO* | YES | YES | Technical |
| QA Review | NO | YES | YES | Technical |
| Approve Product | NO | NO | YES | NO |
| Reject Product | NO | YES | YES | NO |
| Activate Product | NO | NO | YES | NO |
| Archive Product | NO | NO | YES | NO |
| Identity verification | NO | YES | YES | NO |

\* Subject to the final implementation permission matrix.

Technical administration MUST NOT bypass Product governance controls.

---

## 17. No Bypass Rule

No generic endpoint, database operation, administrative shortcut, or direct field mutation may bypass:

- lifecycle validation
- permission checks
- QA requirements
- Evidence readiness
- identity requirements
- approval requirements
- audit recording

Any bypass constitutes a contract violation.

---

## 18. Mandatory Tests

Implementation MUST include tests covering at minimum:

1. Authorized Product edit
2. Unauthorized Product edit
3. Immutable field protection
4. Invalid lifecycle transition
5. Submit workflow
6. QA workflow
7. Approval workflow
8. Rejection workflow
9. Activation gating
10. Identity verification
11. Evidence readiness gating
12. Blocking conflict handling
13. Audit record creation
14. Before/after mutation history
15. Permission enforcement
16. Generic PATCH bypass prevention
17. Evidence mutation traceability

---

## 19. Acceptance Criteria

P4 V1 is considered complete only when:

- Product lifecycle is enforced
- Product governance permissions are enforced
- Submit exists and is controlled
- QA workflow exists
- Approval exists and is controlled
- Reject exists and requires a reason
- Activation is gated
- Identity verification is governed
- Evidence readiness participates in approval gating
- Product mutation audit trail exists
- Product history exists
- Evidence mutations affecting governance are traceable
- Mandatory tests pass

---

## 20. Status Vocabulary

The following lifecycle states are canonical for P4 V1:

- DRAFT
- SUBMITTED
- QA_REVIEW
- APPROVED
- ACTIVE
- REJECTED
- ARCHIVED

No additional lifecycle state may be introduced without Change Control.

---

## 21. P3 Boundary

P3 remains frozen until its contract is formally accepted.

P4 Contract approval does not constitute approval to implement unaccepted P3 functionality.

No implementation may infer requirements from audit findings alone.

---

## 22. Change Control

Any change to this contract requires:

1. Explicit PO decision
2. Contract version update
3. Change documentation
4. Repository update
5. Relevant implementation/test impact review

Future versions may revise V1 decisions where justified.

---

## 23. PO Decision

The Product Owner approves the above eight governance decisions as the V1 basis for P4:

1. Product Edit Governance
2. Product Lifecycle
3. Role and Permission Model
4. Evidence → QA → Approval → Activation Gate
5. Identity Verification
6. Product Mutation Audit Trail
7. Product History
8. Evidence API Governance

---

## 24. Gate Status

**P4 CONTRACT: APPROVED FOR IMPLEMENTATION**

Implementation must follow this contract exactly.

No assumption, invented schema, invented status, or undocumented bypass is permitted.

---

## 25. Implementation Instruction

Implementation teams MUST first verify the current repository state against this contract.

Existing functionality may be reused only where it demonstrably satisfies the contract.

Any gap between the current repository and this contract MUST be explicitly identified and closed through controlled implementation.

**NO ASSUMPTION. NO INVENTED DATA. MASTER IS SOURCE OF TRUTH.**
