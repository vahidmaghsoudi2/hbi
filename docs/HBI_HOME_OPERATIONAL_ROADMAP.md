# HBI — Home & Operational Experience Roadmap

**Status:** APPROVED BY PO  
**Date:** 5 Shahrivar 1405 (2026-08-27)  
**Source of Truth:** GitHub master  
**Integration Owner:** ChatGPT2  
**PO:** Vahid Maghsoudi  

---

## 1. Governing Principle
"Every screen must correspond to a real user, a real decision, or a real action."
- NO FAKE DATA
- NO ASSUMPTION
- NO UI-DRIVEN SCHEMA INVENTION
- CURRENT MASTER IS THE TECHNICAL SOURCE OF TRUTH

## 2. Target Information Architecture
- **PUBLIC EXPERIENCE (/)**: HBI introduction, Trust, Verified catalogue, Consultation entry.
- **PILOT EXPERIENCE (/pilot)**: Controlled pilot workflow.
- **MAQSOUDI OPERATIONAL EXPERIENCE (/workspace)**: Attention Required, Product Workspace, Evidence Review, Product Intake, Operational Status.

## 3. Phased Execution Plan
- **Phase H0**: Reality Reconciliation (Confirm current HEAD, Models, APIs).
- **Phase H1**: Public Home Consolidation (No fake analytics/CRM).
- **Phase H2**: Operational Workspace Foundation.
- **Phase H3**: Home Stats and Attention Contract (GET /api/v1/stats/home).
- **Phase H4**: Product Intake Vertical Slice.
- **Phase H5**: Evidence and Product Review Workspace.
- **Phase H6**: Consultation Experience.
- **Phase H7**: Version Next Expansion (Auth, OTP, Barcode, Images, Search).

## 4. Team Responsibilities
- **ChatGPT2**: Integration Architect, Public/Operational separation, No Fake Data enforcement.
- **DeepSeek2**: Backend Reality, Models/Services verification, API dependency mapping.
- **Qwen1**: Data Contract QA, Stored vs Computed distinction, Duplicate-count prevention.

## 5. Qwen1 Official Verdict
✅ **APPROVED** with one condition: Phase H3 (Home Stats Contract) must be formally defined by Qwen1 before implementation to ensure all values are traceable to existing Models without creating new DB fields for display convenience.

---
**Document Status:** REGISTERED IN GITHUB  
**Decision Authority:** Product Owner (مهندس مقصودی)