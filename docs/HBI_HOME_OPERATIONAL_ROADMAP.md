# HBI — Home & Operational Experience Roadmap

**Status:** APPROVED BY PO  
**Date:** 5 Shahrivar 1405 (2026-08-27)  
**Source of Truth:** GitHub master  
**Integration Owner:** ChatGPT2  
**PO:** Vahid Maghsoudi  
**Qwen1 Verdict:** APPROVED with condition (H3 contract must be defined)

---

## 1. Purpose

HBI is not a conventional online store or decorative dashboard.

Core operational chain:
Customer → Case → Evidence/Knowledge → Reasoning → Recommendation → Product/Inventory → Outcome

Two fundamentally different audiences:
1. Public / Gallery User
2. Maqsoudi as Product Owner and Daily System Operator

These audiences must not be forced into the same interface.

---

## 2. Target Information Architecture

HBI EXPERIENCE
├── PUBLIC EXPERIENCE
│   ├── / (HB introduction + Trust + Verified catalogue + Consultation entry)
│   ├── /consultation (Customer consultation journey)
│   └── /recommendation (Recommendation result/journey)
├── PILOT EXPERIENCE
│   └── /pilot (Controlled pilot workflow)
└── MAQSOUDI OPERATIONAL EXPERIENCE
    └── /workspace
        ├── Attention Required
        ├── Product Workspace
        ├── Evidence Review
        ├── Product Intake
        ├── Consultation Entry
        └── Operational Status

---

## 3. Home Page Philosophy

Public Home answers: "What is HBI, why trust it, what products exist, how to receive guidance?"
Operational Workspace answers: "What needs my attention today, and what can I do next?"

Public Home ≠ Operator Dashboard

---

## 4. Phased Execution Plan

### Phase H0 — Reality Reconciliation
Confirm current HEAD, Models, APIs, Frontend routes.
Owner: ChatGPT2 | Supporting: DeepSeek2, Qwen1

### Phase H1 — Public Home Consolidation
Transform existing / into stable public entry point.
Out of Scope: Fake analytics, CRM, Sales dashboard, Inventory dashboard

### Phase H2 — Operational Workspace Foundation
Separate workspace for Maqsoudi's daily work.
Sections: Attention Required, Product Workspace, Consultation Entry, Operational Status

### Phase H3 — Home Stats and Attention Contract
GET /api/v1/stats/home
QWEN1 RESPONSIBILITY: Define exact response contract from current Models/Services.
Must distinguish Stored vs Computed states.

### Phase H4 — Product Intake Vertical Slice
Enable Maqsoudi to bring real gallery products into HBI.
Required: POST /products, PATCH /products/{id}

### Phase H5 — Evidence and Product Review Workspace
Turn Product/Evidence review into understandable operational workflow.

### Phase H6 — Consultation Experience
Coherent journey: Customer → Profile/Need → Case → Reasoning → Recommendation → Product

### Phase H7 — Version Next Expansion
Only after operational foundation is stable:
- Production authentication
- OTP/Login
- Barcode expansion
- Product images
- Search and filtering
- Sales/Gallery Operations integration

---

## 5. Team Responsibilities

### ChatGPT2 — Integration Architect & Home Experience Owner
Final information architecture, Public/Operational separation, Cross-layer integration, No Fake Data enforcement

### DeepSeek2 — Backend Reality & Implementation Owner
Repository verification, Models/Services reality, Attention Queue query design, API dependency mapping

### Qwen1 — Data Contract & Definition QA Owner
Operational state definitions, Stored vs Computed distinction, Contract consistency, Duplicate-count prevention, CURRENT vs PROPOSED identification

---

## 6. Working Method

CURRENT REPOSITORY → DeepSeek2 (Backend Reality) → Qwen1 (Data Contract Validation) → ChatGPT2 (Integration & UX) → PO (Decision) → Implementation → Integration Review

No independent architecture changes. No parallel speculative redesign. No fake data.

---

## 7. Governing Principle

"Every screen must correspond to a real user, a real decision, or a real action."

NO FAKE DATA
NO ASSUMPTION
NO UI-DRIVEN SCHEMA INVENTION
CURRENT MASTER IS THE TECHNICAL SOURCE OF TRUTH

---

## 8. Qwen1 Official Comments

✅ APPROVED with one condition:
Phase H3 (Home Stats Contract) must be formally defined by Qwen1 before implementation.

Proposed contract for GET /api/v1/stats/home:
- products_need_review_count (Computed from identity_status = NEEDS_REVIEW)
- products_conflict_count (Computed from identity_status = CONFLICT)
- products_missing_evidence_count (Computed from Evidence gaps)
- active_recommendations_count (Stored from Recommendation table)
- system_capabilities (Static list of operational capabilities)

All values must be traceable to existing Models. No new DB fields for display convenience.

---

**Document Status:** REGISTERED IN GITHUB  
**Decision Authority:** Product Owner (مهندس مقصودی)  
**Qwen1 Verdict:** APPROVED WITH CONDITION