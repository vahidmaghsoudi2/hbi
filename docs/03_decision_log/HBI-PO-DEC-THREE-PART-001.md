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

### Product-information path and source of truth

1. The Product Owner (PO) introduces the product and supplies the required instructions, standards, scope, direction and acceptance criteria.
2. Research systems collect and organize the requested information in the Encyclopedia workflow against those requirements. Material that fails the stated standards is corrected, kept explicitly uncertain or rejected; it is not silently accepted.
3. The **Approved Encyclopedia** is the primary, live and human-editable reference for approved product knowledge. It is where the accepted human-readable knowledge is organized and maintained.
4. Original manufacturer disclosures, physical package text, technical documents and relevant scientific sources remain primary source records. They are never deleted or replaced by an Encyclopedia summary; important statements remain traceable to the original source and its limitations.
5. Evidence and Source Traceability support the provenance and review of statements. They are not a parallel product bank, a fourth architecture part or a separate approval gate.
6. **ProductKnowledge** remains the single operational runtime bank that supplies accepted product information to HBI.

**Approved Encyclopedia → Evidence / Source Traceability → ProductKnowledge → Consultation**

**The PO's approval completes product-information acceptance. Do not add another approval or QA gate after it.** Quality checking is part of research, review and acceptance; it is not a duplicate post-approval stage. Independent safety and lifecycle controls remain in force.

This source-of-truth refinement is recorded by the PO decision `HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001` in [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406#issuecomment-6989651765). It does not add a top-level architecture part or authorize runtime/schema/API/database changes.

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
