# ورود محصولات پوستی

**English secondary title (repo path only):** Skin Product Intake  
**Document ID:** HBI-SKIN-PRODUCT-INTAKE-STRATEGIC-BASELINE-v0.1  
**Status:** STRATEGIC DESIGN BASELINE / PRE-IMPLEMENTATION  
**Implementation:** NOT AUTHORIZED  
**Schema / API / Enum / Ontology / Recommendation Engine:** NOT AUTHORIZED  
**Baseline Master (context at registration):** `7e90681e587c228949eac57d2e1e8d52ae351e7a`

| Field | Value |
|-------|--------|
| Purpose | تثبیت جهت معماری، اصول تصمیم‌گیری Skin، مرز پزشکی/Safety/Need/Recommendation |
| Type | Strategic Design Baseline |
| Implementation | **Not Authorized** |
| Next path | Reality Mapping → Contracts A/B/C → Skin Problem Universe |

> این سند **مجوز Implementation نیست**. وجود مفهوم در این سند به‌تنهایی الزام به پیاده‌سازی نیست.

---

## 1. هدف

این سند:

- جهت معماری ورود محصولات پوستی را تثبیت می‌کند.
- اصول تصمیم‌گیری Skin را ثبت می‌کند.
- مرز پزشکی، Safety، Need و Recommendation را مشخص می‌کند.
- مبنای Reality Mapping و Contractهای بعدی است.

این سند **نیست**:

- طراحی دیتابیس
- قرارداد API اجرایی
- پیاده‌سازی enum/ontology
- تغییر موتور Recommendation

---

## 2. هسته تصمیم (مفهومی)

```text
Customer Language
        ↓
Skin Problem Representation
        ↓
Context + Provenance
        ↓
Clinical Relevance
        ↓
Medical / Safety Decision Boundary
        ↓
Decision State
        ↓
Action
        ↓
Need Candidate
        ↓
Product Decision Eligibility
        ↓
Evidence
        ↓
Recommendation
```

این نمودار **workflow کاملاً خطی** تفسیر نشود.

به‌خصوص:

```text
Problem Representation
        ↓
   ┌────┴────┐
   ↓         ↓
 Need     Safety/Scope
   └────┬────┘
        ↓
 Decision
```

Need و Safety ممکن است بر اساس یک Problem Representation مشترک و اطلاعات تکمیلی شکل بگیرند.

---

## 3. اصول غیرقابل مذاکره

### 3.1 Customer Statement ≠ Diagnosis

HBI می‌تواند گزارش مشتری را برای تصمیم‌سازی معناگذاری و ساختاربندی کند، اما از آن تشخیص پزشکی تولید نمی‌کند.

```text
CUSTOMER_REPORTED
≠
CLINICIAN_DOCUMENTED
≠
SYSTEM_DERIVED_HYPOTHESIS
```

و:

```text
SYSTEM_DERIVED_HYPOTHESIS ≠ DIAGNOSIS
```

### 3.2 Skin Finding باید از Symptom جدا باشد

حداقل این مفاهیم باید قابل تفکیک باشند:

```text
SYMPTOM
SKIN_FINDING
CONCERN
GOAL
KNOWN_CONDITION
DIAGNOSIS
```

همچنین:

```text
SYMPTOM ≠ DIAGNOSIS
SKIN_FINDING ≠ DIAGNOSIS
CONCERN ≠ DIAGNOSIS
NEED ≠ DIAGNOSIS
```

### 3.3 Provenance الزامی است

منبع هر assertion پزشکی/پوستی باید قابل تشخیص باشد:

```text
CUSTOMER_REPORTED
CLINICIAN_DOCUMENTED
OBSERVED_BY_OPERATOR
SYSTEM_DERIVED_HYPOTHESIS
UNKNOWN
```

### 3.4 Clinical Relevance یک Entity یا Diagnosis Engine نیست

`Clinical Relevance` در این مرحله صرفاً یک **derived assessment** است.

سه سؤال اصلی:

```text
Does this change Safety?
Does this change Required Information?
Does this change HBI Scope?
```

بنابراین:

```text
Clinical Relevance → Decision Impact
```

نه:

```text
Clinical Relevance → Disease Guess
```

### 3.5 Severity باید provenance داشته باشد

```text
CUSTOMER_REPORTED_SEVERITY / IMPACT
≠
CLINICAL_SEVERITY
```

HBI نباید صرفاً از برداشت ذهنی مشتری، شدت پزشکی قطعی استخراج کند.

### 3.6 Medical Context ≠ Medical Referral

وجود سابقه یا diagnosis پزشکی به‌خودی‌خود معادل referral نیست.

```text
Medical Context ≠ Medical Referral
```

Referral باید نتیجه Decision Boundary باشد.

### 3.7 Safety فقط Red Flag نیست

Decision Boundary حداقل این ابعاد را در نظر می‌گیرد:

```text
Risk
Context
Uncertainty
HBI Scope
Evidence Sufficiency
```

Red Flag صرفاً یکی از input/signalهای تصمیم است.

### 3.8 Decision State ≠ Action

```text
DECISION STATE → ACTION
```

نمونه‌های مفهومی (enum نهایی **پیاده‌سازی نشود**):

```text
INSUFFICIENT_INFORMATION → ASK
MEDICAL_REVIEW_INDICATED → REVIEW / REFER
UNSAFE_FOR_PRODUCT_RECOMMENDATION → WITHHOLD
SUFFICIENT_FOR_CARE → CARE
```

### 3.9 UNKNOWN فعلاً taxonomy نهایی ندارد

اصل وجود وضعیت epistemic uncertainty پذیرفته است؛ taxonomy نهایی **باز** است.

نمونه‌های بررسی‌شده (Contract اجرایی نیستند):

```text
NOT_PROVIDED
UNAVAILABLE
NOT_ESTABLISHABLE_BY_HBI
```

### 3.10 Need یک Diagnosis Proxy نیست

Need یک **care/recommendation-relevant need candidate** است.

```text
Clinical Interpretation ≠ Need
Need Detected ≠ Recommendation Allowed
```

### 3.11 No Product Recommendation یک خروجی معتبر است

```text
Customer Problem → Decision → NO PRODUCT RECOMMENDATION
```

یا:

```text
Customer Problem → Medical Boundary → REFER
```

فرض معماری نیست که هر Problem الزاماً به Product ختم شود.

### 3.12 Evidence فقط یک مرحله انتهایی نیست

Evidence یک **cross-cutting evidence/provenance layer** است:

```text
Customer-side reasoning  ↔  Evidence
Product Knowledge        ↔  Evidence
Safety / Medical Decision ↔  Evidence
Product Eligibility      ↔  Evidence
```

### 3.13 Customer Eligibility و Product Eligibility جدا باشند

```text
CUSTOMER DECISION ELIGIBILITY
+ PRODUCT ELIGIBILITY
+ EVIDENCE READINESS
+ SAFETY / SCOPE CLEARANCE
        ↓
RECOMMENDATION PERMITTED
```

```text
Customer Problem ≠ Product Required
Need Detected ≠ Recommendation Allowed
```

### 3.14 Problem Representation فعلاً Domain Entity مستقل نیست

فعلاً صرفاً **Domain Representation / Decision Context** است.

محل persistence (Case، Conversation، …) باید بعداً از Reality Mapping تعیین شود. از طراحی مطلوب، ساختار فعلی Repository فرض نشود.

### 3.15 Decision State فعلاً Runtime-derived تلقی شود

```text
Decision State = derived from current inputs
```

بدون Contract مستقل نباید به‌عنوان حقیقت دائمی Case ذخیره شود.

در آینده، در صورت نیاز، Decision Outcome / Decision Trace می‌تواند شامل باشد:

```text
Inputs, Provenance, Evidence, Decision, Action, Timestamp, Decision Basis
```

---

## 4. سه Contract بعدی

```text
A. SKIN PROBLEM REPRESENTATION
B. SKIN MEDICAL / SAFETY DECISION BOUNDARY
C. SKIN PRODUCT DECISION ELIGIBILITY
```

پس از بررسی این سه:

```text
Decision Architecture
        ↓
Canonical Concepts
        ↓
Skin Problem Universe
```

**نه برعکس.**

---

## 5. Reality Rule

> هیچ ادعایی درباره وضعیت فعلی HBI نباید صرفاً بر اساس اسناد قدیمی، گزارش Agentها یا طراحی قبلی پذیرفته شود.

Reality Mapping بعدی باید با شواهد فعلی Repository انجام شود:

```text
Current HEAD / SHA
File
Symbol
Data Flow
Test
CI
```

و هر تفاوت میان:

```text
DESIGNED
IMPLEMENTED
TESTED
VERIFIED
```

صریحاً مشخص شود.

---

## 6. Implementation Ban (این Baseline)

```text
NO CODE
NO SCHEMA CHANGE
NO MIGRATION
NO API CHANGE
NO ENUM IMPLEMENTATION
NO RECOMMENDATION ENGINE CHANGE
NO ONTOLOGY IMPLEMENTATION
```

---

## 7. Document Control

| Item | Value |
|------|--------|
| Title (searchable) | **ورود محصولات پوستی** |
| Status | STRATEGIC DESIGN BASELINE / PRE-IMPLEMENTATION |
| Implementation | NOT AUTHORIZED |
| Repo path | `docs/architecture/SKIN_PRODUCT_INTAKE_STRATEGIC_BASELINE_v0.1.md` |

**End of Baseline v0.1**
