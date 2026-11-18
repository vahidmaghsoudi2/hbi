# HBI Architecture

**Last Updated:** 2026-11-18  
**Architecture authority:** [HBI-PO-DEC-THREE-PART-001](../03_decision_log/HBI-PO-DEC-THREE-PART-001.md)

## The HBI model

HBI has three main parts. Keep the architecture and the working path centered on these parts:

1. **ProductKnowledge** — what the system reliably knows about each product.
2. **Customer Context** — the customer's relevant profile, history, current condition and need.
3. **Intelligence & Response** — the system connects the product information with the customer's context, analyses their fit and limitations, and gives an appropriate response.

The purpose is to make this connection accurate, safe, dependable, smooth and fast. Do not turn internal evidence handling, review activities or technical implementation details into additional top-level architecture parts.

## 1. ProductKnowledge

ProductKnowledge is the single product-information bank used by HBI.

A product is researched before entry. The Product Owner supplies the product and the required instructions, standards, scope and acceptance criteria to multiple AI research systems. They collect and organize the requested product information. Information that does not meet the stated requirements is rejected or corrected before acceptance. The Product Owner reviews and approves the completed product information. After that approval, the product information is ready to be entered into ProductKnowledge and used by the system.

**Approval is part of preparing the information for entry, not another gate after entry.** Do not create separate Evidence, Encyclopedia and QA repositories or sequential approval barriers for the same product-information intake.

Sources and supporting evidence remain attached or traceable where relevant, so that the origin and limits of important information can be checked. They support the reliability of ProductKnowledge; they are not a second product bank or a separate user-facing workflow.

## 2. Customer Context

Customer Context contains the information needed to understand the person and the current consultation:

- The customer's relevant profile and stable information.
- Relevant skin/hair condition and history.
- The customer's current need, request and reported concerns.
- Information recorded or confirmed for the current consultation by the gallery operator, consultant or clinician, as applicable.

Keep persistent customer information distinct from the current consultation details, but treat both as one Customer Context part of the HBI model. Collect and use personal information only with an appropriate basis and access controls.

## 3. Intelligence & Response

This is the part that connects ProductKnowledge and Customer Context.

It should understand the customer's need, retrieve relevant product facts, assess suitability and limitations, recognize risks or missing/contradictory information, and produce a clear response appropriate to that customer.

When reliable information is insufficient or a medical warning sign or high-risk situation is present, it must not invent certainty or force a product recommendation. It should ask for the necessary information, explain the limitation or direct the customer to an appropriate healthcare professional.

## Product-intake completion rule

The practical product-intake path is:

Product supplied + PO standards/instructions → AI research and compilation → review against the stated requirements → PO approval → ProductKnowledge entry and availability for system use.

Do not add a second QA approval stage after the PO has accepted the prepared product information. Any correction or later change follows the same clear review-and-approval responsibility; it does not justify creating parallel banks or unnecessary gates.

## Simplicity and implementation rules

- Keep these three parts as the complete top-level architecture.
- Every additional component, filter, approval or process must solve a concrete, demonstrated problem. If it does not, do not add it.
- Do not split one product-information intake into multiple repositories, repeated reviews or duplicate approvals.
- Preserve scientific accuracy, source traceability, privacy and safety without making them separate obstacles to routine work.
- Prefer the shortest reliable path that lets the team introduce a product and use it in a customer consultation.
- Do not claim a capability is implemented unless repository code and relevant tests/evidence verify it.

## Existing backend structure

The repository may contain models, repositories, services, interfaces and domain-specific gates. These are implementation details, not additional top-level business pillars. Preserve existing contracts and safety requirements unless a separately authorized change is made. Do not create or change schema, APIs, UI, runtime behavior or production data as a consequence of this documentation decision alone.

## Scope

This document records the agreed target architecture and product-intake principle. It does not claim that the complete three-part connection is already implemented, and it does not authorize runtime, schema, API, UI, database, product-data or customer-data changes.
