# S01 Non-Production Acceptance Test Cases — Proposal v0.1

**Status:** PROPOSED / NON-PRODUCTION ONLY  
**Parent:** PR #416  
**Purpose:** Make the proposed S01 data/provenance rules testable before any implementation. These cases do not approve customer-facing questions, clinical classification, referral rules, production schema, or product recommendations.

## Execution boundary

- Run only against fixtures or an isolated test environment; do not write to the production database.
- Do not use real customer data.
- Expected outcomes below validate data handling and governance, not medical conclusions.
- P01 remains `Scoped / Deferred`; P02 remains `Identified + Linked / Undetermined`; P05, P06 and P07 remain unchanged.
- No numeric confidence score, automated problem acceptance, product suitability inference, or referral threshold is permitted.

## Test matrix

| ID | Fixture / action | Expected result | Failure condition |
|---|---|---|---|
| S01-T01 | Customer reports “my skin feels tight after washing” | Store the original report as `CUSTOMER_REPORT`; preserve question/version and entry time. No automatic P01/P02 acceptance. | Report is stored as a diagnosis or changes a problem status. |
| S01-T02 | Customer selects “not sure” | Store an explicit unknown response state; do not convert it to “no”. | Unknown becomes false/negative, empty, or an inferred value. |
| S01-T03 | Customer skips a question | Store `SKIPPED`; distinguish it from `NOT_ASKED` and `UNKNOWN`. | Skipped is interpreted as symptom absent. |
| S01-T04 | A question was not presented in this version of the intake | Store `NOT_ASKED` and the question-set version. | The system claims the customer answered or skipped it. |
| S01-T05 | Customer reports a symptom; operator records a different observation | Preserve two separately attributed records and their timestamps; mark discrepancy for review where supported. | One source overwrites the other or provenance is lost. |
| S01-T06 | Instrument value supplied without unit or method/device | Mark measurement incomplete or uninterpretable; do not compare it to a threshold. | A threshold or classification is applied despite missing context. |
| S01-T07 | No instrument measurement was performed | Store `NOT_MEASURED` or the approved equivalent; do not estimate a value. | Missing measurement is replaced by a guessed number or “normal”. |
| S01-T08 | Free text contains “dehydrated skin” | Preserve the customer’s words as a report; do not accept P02 from the wording alone. | The phrase automatically sets P02 to accepted/classified. |
| S01-T09 | Customer reports oily skin and tightness | Preserve each reported dimension separately; do not use oiliness alone to accept or reject P02. | Oiliness is treated as proof against/for P02. |
| S01-T10 | Manufacturer product page says “hydrates dry skin” | Record only as a manufacturer claim with source and claim origin. | Marketing wording is stored as independent scientific evidence or as customer suitability. |
| S01-T11 | Product and problem share an ingredient or keyword | Do not create a problem-to-product relationship without an explicitly typed, reviewed evidence record. | Keyword/ingredient overlap creates an accepted relationship or recommendation. |
| S01-T12 | Evidence record lacks a usable source reference or source type | Keep it incomplete/pending review; identify missing provenance. | Unsupported evidence is marked accepted. |
| S01-T13 | Two sources make conflicting statements | Preserve both sources, their provenance, and the conflict state; do not silently choose one. | Conflict is erased or one source is silently preferred. |
| S01-T14 | Reviewer corrects an interpretation | Preserve prior value, new value, reviewer role, date/time, and rationale. | Previous value or audit rationale is lost. |
| S01-T15 | No approved safety/referral protocol is available | Keep the gate open; do not generate a new trigger or threshold. | The draft questions create an unapproved referral decision. |
| S01-T16 | All proposed questions receive answers | Store answers only; keep problem statuses unchanged unless a separate approved and validated rule exists. | Completing the form automatically accepts P01/P02 or triggers product advice. |

## Required test evidence

For each executed case, record:

- test ID and fixture identifier (no personal data);
- software/contract version and environment;
- observed result and pass/fail;
- evidence artifact or log reference;
- defect/exception and owner, if any.

A case is **not verified** until its execution evidence is recorded. A prose expectation, green CI run, or browser proof alone does not prove that every case was exercised.

## Acceptance gate

This proposal is ready for implementation planning only after the PO confirms the data-handling requirements and the implementation owner maps each case to a test. Any case involving clinical terminology, interpretation, measurements, or safety/referral remains subject to qualified medical review. No case in this document authorizes production rollout.
