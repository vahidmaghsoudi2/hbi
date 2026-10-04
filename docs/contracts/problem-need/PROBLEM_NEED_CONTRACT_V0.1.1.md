# HBI Problem → Need Contract V0.1.1

Status: ACCEPTED WITH CONDITIONS — awaiting final independent baseline verification

## 1. Purpose

This contract defines when HBI may move from a recorded Problem / Presentation to a Customer Need during consultation.

This is a contract-definition artifact. It does not execute Need Extraction.

Core boundaries:

- Problem ≠ Need
- Need ≠ Diagnosis
- Need ≠ Product
- Need ≠ Treatment
- Need ≠ Recommendation

## 2. Scope

The contract governs:

Recorded Problem / Presentation
→ Evidence and Context review
→ Candidate Need
→ Eligibility decision

Permitted outcomes:

- ELIGIBLE
- CANDIDATE / PENDING EVIDENCE
- NOT DETERMINABLE FROM PROBLEM ALONE

Eligibility is case-specific.

**Eligible remains case-specific; no label-level Need table is derived from this Contract.**

## 3. Definitions

Problem / Presentation:
A recorded issue, state, symptom, manifestation, or concern within HBI scope.

Candidate Need:
A Consultation Concern that may legitimately become a Need, subject to evidence and boundary checks.

Eligible Need:
A Candidate Need for which the required Recorded Consultation Evidence and all contract boundaries are satisfied.

Recorded Consultation Evidence:
Information actually recorded in the Profile or Consultation and traceable to that record.

Medical Existence:
Evidence that a condition exists in medical/scientific knowledge. This does not, by itself, establish an HBI Need.

Prevalence:
Evidence that a Problem is common. This does not, by itself, establish an HBI Need.

## 4. Problem → Need Boundary

A Problem Label alone cannot create an Eligible Need.

Eligibility requires:

1. a recorded Problem / Presentation; and
2. additional Recorded Consultation Evidence relevant to the Candidate Need; and
3. satisfaction of the evidence, boundary, and no-assumption rules.

Minimum evidence package:

- E-EXIST
- E-REL-HBI
- observational / non-diagnostic framing
- medical_boundary
- unknowns
- E-CL = NOT VERIFIED in V1

E-EXIST alone ≠ Accepted HBI Need.

## 5. Candidate Need Wording

Candidate Need must remain at Consultation Concern level.

It must not encode:

- Product
- Product selection
- Treatment
- Treatment choice
- Recommendation
- Recommendation scoring

Examples of prohibited Need wording:

- treatment of dryness
- select Product X
- prescribe medication
- recommend a specific anti-redness product

These belong to later Product, Treatment, or Recommendation logic.

## 6. Candidate → Eligible Lock

The following are insufficient by themselves:

- Problem Label
- medical existence
- prevalence
- generic HBI relevance
- assumed customer importance
- synthetic customer language

The following may support eligibility:

Problem Label + sufficient Recorded Consultation Evidence + all applicable boundary checks.

Eligibility is therefore Consultation-specific, not Label-specific.

## 7. No-Assumption Rules

Only information actually recorded in Profile / Consultation may affect Need eligibility.

The Contract must not infer automatically:

- cause
- severity
- diagnosis
- customer preference
- priority
- treatment
- product
- recommendation

Customer Statement ≠ Operator Interpretation ≠ Clinical Interpretation ≠ System Inference.

Symptom / Manifestation may be a signal or limited Candidate Concern, but:

Symptom alone ≠ Accepted Need.

## 8. Customer Language / Reality

CL-V1 = DEFERRED.

E-CL = NOT VERIFIED.

Customer Reality = NOT VERIFIED.

Synthetic Customer Language is not Customer Evidence.

## 9. Safety / Clinical Boundary

Problems requiring clinical/safety handling must not be converted into ordinary Eligible Needs from their labels alone.

P49, P50, and P52–P56 retain explicit clinical/safety boundaries.

P51 is:

- Classification: Discovery Problem / Context
- V1 Need Eligibility: NOT ELIGIBLE FROM PROBLEM ALONE
- Safety/Referral: NO

## 10. Multiple Needs and Priority

Multiple Problems may support one shared Consultation Concern.

One Problem may support multiple Candidate Needs only where each has independent supporting evidence.

Priority must not be inferred from:

- prevalence
- general medical seriousness
- generic HBI relevance
- product availability
- commercial value
- operator assumption

Priority requires recorded Consultation Evidence.

## 11. Contractual Test Fixtures

These are Contract Test Fixtures, not real customer Cases.

### Fixture A — P01 alone

Problem:

P01 Dry skin / Xerosis

Additional Recorded Consultation Evidence:

None.

Decision:

CANDIDATE / PENDING EVIDENCE

or, where a final Need cannot be determined:

NEED = NOT DETERMINABLE FROM PROBLEM ALONE

Must not infer cause, severity, priority, treatment, product, or recommendation.

Acceptance Test:

P01 alone must not become ELIGIBLE.

### Fixture B — P24 alone

Problem:

P24 Persistent redness

Additional Recorded Consultation Evidence:

None.

Decision:

CANDIDATE / PENDING EVIDENCE

or:

NEED = NOT DETERMINABLE FROM PROBLEM ALONE

Must not infer rosacea, another diagnosis, cause, severity, treatment, product, or priority.

Acceptance Test:

P24 alone must not become ELIGIBLE.

### Fixture C — P49 / P50

Problem:

P49 Changing mole
or
P50 New/Growing Skin Lesion

Additional Recorded Consultation Evidence:

None.

Decision:

NOT ELIGIBLE FROM PROBLEM ALONE

Safety / Clinical Boundary:

Clinical/Safety handling remains explicit.

Must not infer benignity, malignancy, treatment, product, reassurance, or urgency beyond recorded evidence.

Acceptance Test:

P49/P50 alone must never automatically produce an ordinary Eligible Customer Need.

## 12. Problem Group Mapping

### Group 1 — Barrier / Hydration / Surface
P01, P02, P03, P04, P05, P06, P07

Default:
NEED = NOT DETERMINABLE FROM PROBLEM ALONE

### Group 2 — Acne / Follicular
P08, P09, P10, P11, P12, P13, P14, P15, P16

Default:
CANDIDATE / PENDING EVIDENCE

### Group 3 — Pigment / Color
P17, P18, P19, P20, P21, P22, P23

Default:
NEED = NOT DETERMINABLE FROM PROBLEM ALONE

### Group 4 — Redness / Inflammation / Rash
P24, P25, P26, P27, P28, P29, P30, P31, P32, P33

Default:
CANDIDATE / PENDING EVIDENCE

### Group 5 — Infection / Infestation
P34, P35, P36, P37, P38, P39, P40, P41, P42

Default:
NEED = NOT DETERMINABLE FROM PROBLEM ALONE

### Group 6 — Texture / Keratinization / Lesions
P43, P44, P45, P46, P47, P48, P49, P50

P43–P48:
CANDIDATE / PENDING EVIDENCE

P49–P50:
NOT ELIGIBLE FROM PROBLEM ALONE

### Group 7 — UV Damage / Suspicious Lesions
P51, P52, P53, P54, P55, P56

P51:
Discovery Problem / Context
V1 Need Eligibility = NOT ELIGIBLE FROM PROBLEM ALONE
Safety/Referral = NO

P52–P56:
Clinical/Safety boundary applies.

### Group 8 — Systemic / Autoimmune / Clinically Significant
P57, P58, P59, P60, P61

Default:
NEED = NOT DETERMINABLE FROM PROBLEM ALONE

This mapping is a contract grouping, not Need Extraction and not a Problem → Automatic Need table.

## 13. Acceptance Tests

AT-01 — Label Alone:
Problem Label alone MUST NOT create ELIGIBLE Need.

AT-02 — Medical Existence:
Problem + medical existence alone MUST NOT create ELIGIBLE Need.

AT-03 — Prevalence:
Problem + prevalence alone MUST NOT create ELIGIBLE Need.

AT-04 — Recorded Evidence:
Problem + sufficient Recorded Consultation Evidence MAY become ELIGIBLE if all boundaries pass.

AT-05 — Product Leakage:
Candidate Need containing Product / Selection / Recommendation logic MUST be rejected or rewritten to Consultation Concern level.

AT-06 — Treatment Leakage:
Candidate Need that prescribes or implies treatment MUST NOT be accepted as a Need.

AT-07 — Diagnosis Leakage:
Eligibility requiring an inferred diagnosis not recorded in Consultation MUST fail.

AT-08 — P49/P50 Safety:
P49 or P50 alone MUST NOT create an ordinary Eligible Need.

AT-09 — Customer Language:
Synthetic customer wording MUST NOT be treated as E-CL.

AT-10 — Priority:
Problem Label alone MUST NOT establish priority.

AT-11 — Multiple Needs:
Each independently accepted Need MUST have independent supporting evidence.

AT-12 — No Determination:
When required evidence is absent:
NEED = NOT DETERMINABLE FROM PROBLEM ALONE.

## 14. Insufficient Information Handling

Insufficient evidence is a valid Contract outcome.

The Contract must not fill missing information by assumption.

Where evidence is insufficient, the system/operator must retain the appropriate pending or non-determinable state rather than manufacture eligibility.

## 15. What Does Not Constitute a Need

The following do not constitute a Need by themselves:

- diagnosis
- disease name
- symptom label
- product request
- product availability
- treatment choice
- recommendation
- marketing claim
- prevalence
- medical existence
- operator assumption
- synthetic customer language
- assumed preference
- assumed severity
- assumed priority

## 16. Open Questions

- The exact operational definition and storage of Recorded Consultation Evidence remains an implementation-stage question.
- Customer Reality remains NOT VERIFIED.
- CL-V1 remains DEFERRED.
- Customer Profile Contract V1.1 has not been re-registered as part of this Patch.
- Problem Bank admission structure remains outside this Contract.

Recorded Consultation Evidence is therefore an Open Question for implementation, not an Acceptance blocker for this Contract.

## 17. Out of Scope

Explicitly forbidden by this Contract stage:

- Need Extraction
- Customer Case creation
- Product Mapping
- Product Selection
- Recommendation changes
- Recommendation scoring changes
- Problem Bank modification
- Map modification
- Schema/API/UI/DB changes
- Migration
- implementation
- synthetic Customer Language
- Customer Reality claims
- merge

## 18. Governance / Authorization

Contract:
Problem → Need Contract V0.1.1

Management Decision:
ACCEPT WITH CONDITIONS

Independent Management-Gate Verification:
PASS WITH CONDITIONS

Required registration corrections:
1. P48/P49/P50 wording is aligned exactly with the Problem Bank IDs:
   - P48 = Moles / Nevi
   - P49 = Changing Mole
   - P50 = New/Growing Skin Lesion
2. The following condition is binding:
   Eligible remains case-specific; no label-level Need table is derived from this Contract.

Baseline:
PENDING FINAL INDEPENDENT BASELINE VERIFICATION

Contract Acceptance:
ACCEPTED WITH CONDITIONS

Need Extraction:
NOT AUTHORIZED

Product Mapping:
NOT AUTHORIZED

Recommendation:
NOT AUTHORIZED

Implementation:
NOT AUTHORIZED

Merge:
NOT AUTHORIZED
