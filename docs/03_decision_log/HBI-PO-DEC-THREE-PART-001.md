# HBI-PO-DEC-THREE-PART-001 — HBI's Three-Part Model

**Decision date:** 2026-11-18  
**Authority:** Product Owner (PO)  
**Status:** PO DECIDED — DOCUMENTATION PR DRAFT  
**Scope:** HBI top-level architecture and product-information intake  
**Implementation status:** Architecture direction recorded. This document does not claim that the complete workflow or runtime connection is already implemented and does not authorize code, schema, API, UI, database or production-data changes.

## Decision

HBI's main purpose is:

**The system must know what each product actually contains and can do, understand the customer's condition and need, and use the intelligent relationship between those two to provide an appropriate response for that customer.**

The complete top-level HBI model has exactly three parts:

1. **ProductKnowledge** — reliable, approved information about products.
2. **Customer Context** — the customer's relevant profile, condition, history and current consultation need.
3. **Intelligence & Response** — analysis that connects ProductKnowledge with Customer Context and produces an appropriate response.

These three parts are the architecture. Do not add more top-level pillars by renaming supporting activities, records or technical mechanisms.

## 1. ProductKnowledge

ProductKnowledge is the single bank of product information used by HBI.

### Product-intake path

1. The Product Owner (PO) introduces the product and supplies the required instructions, standards, scope, direction and acceptance criteria.
2. Multiple AI research systems are instructed to research and extract the product information according to those requirements.
3. The systems collect and organize the information. Material that fails the stated standards is corrected or rejected; it is not accepted as product information.
4. The PO reviews and approves the prepared product information.
5. After PO approval, the information is ready to enter ProductKnowledge and be used by HBI.

**The PO's approval completes product-information acceptance. Do not add another approval or QA gate after it.** Quality checking is inherent in the research, review and acceptance process. It is not a separate bank or an extra post-approval stage.

Sources and supporting evidence should remain traceable where relevant. They support the reliability and verifiability of the information inside ProductKnowledge; they do not create another top-level architecture part, parallel product bank or separate intake workflow.

## 2. Customer Context

Customer Context contains the relevant information about the customer and the current consultation:

- Relevant customer profile and stable information.
- Relevant skin/hair condition and history.
- Current need, request and reported concerns.
- Current-session information recorded or confirmed by the gallery operator, consultant or clinician, as applicable.

Persistent profile information and the details of the current consultation are distinguishable kinds of information within the same Customer Context part. They are not separate top-level pillars.

Personal information must be collected and used with an appropriate basis and access controls.

## 3. Intelligence & Response

This part connects the two inputs:

**ProductKnowledge + Customer Context → analysis → appropriate customer response**

It must understand the customer's need, retrieve relevant product facts, assess suitability and limitations, recognize risks and missing or contradictory information, and provide a clear, useful response for that customer.

It must not invent certainty or force a recommendation when information is insufficient. For medical warning signs or high-risk situations, it must explain the limitation, request necessary information or direct the customer to an appropriate healthcare professional.

## Simplicity is a binding design rule

The PO explicitly rejects unnecessary complexity, duplicate systems and non-functional barriers that delay the introduction of products or the use of HBI.

Therefore:

- Keep the top-level architecture to the three parts above.
- Do not create separate top-level repositories or pillars named Evidence, Encyclopedia or QA.
- Do not split one product's research, review and acceptance into duplicate banks or repeated approval gates.
- Do not add a process, filter, component or approval unless it solves a concrete and demonstrated problem.
- Keep supporting source references, checks and technical records as simple internal support for ProductKnowledge.
- Prefer a simple, smooth, dependable and fast path that enables the team to introduce a product and use it in customer consultation.
- Do not sacrifice scientific accuracy, customer safety, privacy or honest uncertainty in the name of speed.

## Superseded decision

[HBI-PO-DEC-CKER-001](./HBI-PO-DEC-CKER-001.md) is superseded. Its CKER framing must not be treated as current architecture or used to introduce additional product-intake stages. It remains only as a historical record with an explicit superseded notice.

## Scope and implementation boundary

This is the current PO-approved architecture direction. It does not assert that all three parts are already connected in the running system. It does not authorize runtime, schema, API, UI, database, product-data or customer-data changes. Existing domain contracts and safety controls remain in force unless separately changed through an authorized decision.

## Change record

- Previous framing: CKER as the top-level knowledge/evidence architecture, with separately named knowledge and evidence layers and claim-level QA framing.
- New decision: exactly three top-level parts — ProductKnowledge, Customer Context, Intelligence & Response.
- Reason: keep HBI focused on its real purpose and remove unnecessary complexity and barriers to product introduction.
- Impact: architecture and related navigation documents must point to this decision; the former CKER decision is marked superseded.
- Owner/authority: Product Owner.
- Approval: explicit PO direction recorded on 2026-11-18.
