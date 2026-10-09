# HBI — Dual-Team Operating Contract

**Document ID:** `HBI-DUAL-TEAM-OPS-001`
**Title:** Dual-Team Operating Contract V1.0
**Status:** `DESIGN PROPOSAL` — pending PO acceptance and merge
**Baseline:** `master @ d420b65677f10f5dd5a36a027f810d4615158615`
**Authority:** Product Owner — مهندس مقصودی

---

## 1. Purpose

این سند مدل تقسیم کار دو تیم اصلی HBI را تعریف می‌کند تا مأموریت‌ها در سطح حوزه‌های بزرگ مدیریت شوند و از هماهنگی‌های ریز و موازی‌کاری جلوگیری شود.

این سند جایگزین `PROJECT_RULES.md`، `AGENTS.md`، IOV Policy، Mission Ownership Policy یا تصمیم‌های صریح PO نیست.

---

## 2. Team A — Architecture / Governance / Decision Management

**مالک حوزه:** GPT-5.6

مسئولیت کلی:

- HBI Core و Architecture
- Governance و قوانین پروژه
- GAPهای معماری و تصمیم‌گیری
- Definition و Contract
- Decision Log و وضعیت تصمیم‌ها
- تعیین اینکه چه چیزی نیازمند تصمیم PO است
- آماده‌سازی گزینه‌ها، شواهد و Impact برای PO
- کنترل Design → Authorization → Implementation
- Independent Verification در سطح Architecture / Governance / Decision
- کنترل انطباق مسیر پروژه با Reality و قراردادهای پذیرفته‌شده

**سؤال محوری Team A:**

> HBI چه چیزی است، چه تصمیمی باید گرفته شود، و تحت چه قواعدی باید ساخته شود؟

Team A مالک تصمیم نهایی PO نیست؛ مسئول آماده‌سازی، کنترل و Verification تصمیم است.

---

## 3. Team B — Runtime / Product / Implementation Management

**مالک حوزه:** GPT-1

مسئولیت کلی:

- Runtime Reality Audit
- Model → Repository → Service → Facade → API → DTO → Permission → Audit → History → Tests
- GAPهای اجرایی و Runtime
- Product / Customer / Evidence / Knowledge / Recommendation در سطح Implementation
- Test و Regression
- کشف نقص‌های واقعی Runtime
- اجرای مأموریت‌های 0→100 پس از Authorization
- آماده‌سازی Implementation و Evidence Package
- Post-Implementation Verification

**سؤال محوری Team B:**

> چیزی که HBI تصمیم گرفته، در Repository چگونه وجود دارد و آیا واقعاً درست کار می‌کند؟

---

## 4. Shared Boundary — PO Decision Boundary

موارد زیر بدون تصمیم صریح PO قابل اجرا نیستند:

- Core
- Architecture
- Policy
- Contract
- Scope
- Role / Ownership
- Weight / Ranking / Threshold
- Gate / Filter
- تغییر Business Behavior
- Implementation Authorization

هر تیم می‌تواند موضوع را بررسی و پیشنهاد دهد، اما **PO تصمیم نهایی را می‌گیرد**.

---

## 5. One Task = One Owner = End-to-End

هر مأموریت یک Owner دارد و Owner از Reality Audit تا Evidence و Acceptance را در حوزه خود دنبال می‌کند.

همکاری بین تیم‌ها آزاد است؛ انتقال یا تصاحب خاموش مسئولیت ممنوع است.

اگر یک موضوع هم Architecture و هم Runtime داشته باشد، یک Owner اصلی تعیین می‌شود و تیم دیگر نقش Verification / Input خواهد داشت.

---

## 6. Dual-Team ≠ Talk vs Code

این تقسیم به معنی «Team A فقط حرف بزند» و «Team B فقط کدنویسی کند» نیست.

هر دو تیم باید در حوزه مالکیت خود **0→100** عمل کنند:

- Team A: Reality → Contract → Options → PO Decision → Registration → Governance Verification
- Team B: Runtime Reality → Contract Check → Authorized Design → Implementation → Test → Evidence → Verification

---

## 7. Non-Negotiable Governance

همه فعالیت‌ها تابع قوانین موجود HBI هستند، از جمله:

- `origin/master` تنها Source of Truth
- Reality First
- No Assumption / No Invented Data
- Evidence-bound claims
- `Existence ≠ Usage ≠ Integration ≠ Verified`
- Design Proposal ≠ Contract
- Authorization قبل از Implementation
- Test / Regression / Evidence قبل از Done
- Independent Verification قبل از Acceptance
- PO Acceptance قبل از Merge
- Post-Merge Reality Verification
- Frozen scoring / weighting فقط با تصمیم رسمی قابل تغییر است
- Issue #37 بدون شواهد و تصمیم رسمی بازگشایی/تغییر نمی‌شود

---

## 8. Communication Rule

گزارش‌های تیمی باید:

- یکپارچه و قابل Forward باشند؛
- وضعیت را با `FACT / CONTRACT / DESIGN PROPOSAL / OPEN DECISION / UNKNOWN / CONFLICT` مشخص کنند؛
- Evidence شامل SHA + Path ارائه کنند؛
- از گزارش‌های پراکنده و تکراری پرهیز کنند؛
- اختلاف را صریحاً اعلام کنند؛
- در صورت Block شدن، دلیل، Evidence، SHA، Path و Decision Required را اعلام کنند.

---

## 9. GitHub Rule

Repository:

`vahidmaghsoudi2/hbi`

هر تیم باید Reality را از Repository واقعی بررسی کند و در گزارش، Branch و SHA دقیق را ثبت کند.

**نوشتن روی Repository یا ایجاد تغییر اجرایی بدون Authorization مجاز نیست.**

**Merge به `master` فقط با مجوز صریح PO انجام می‌شود.**

---

## 10. Current Operating Interpretation

این سند صرفاً **مدل عملیاتی پیشنهادی** است و تا زمان PO Acceptance، Contract محسوب نمی‌شود.

این سند:

- GAP جدید ایجاد نمی‌کند؛
- GAP-01..04 را باز نمی‌کند؛
- Issue #37 را تغییر نمی‌دهد؛
- Scoring / Weighting را تغییر نمی‌دهد؛
- Problem / Assessment Entity را الزام نمی‌کند؛
- هیچ Implementation را مجاز نمی‌کند.

---

## 11. Final Operating Model

```text
                 PRODUCT OWNER
                       │
              PO DECISION BOUNDARY
                       │
          ┌────────────┴────────────┐
          │                         │
      TEAM A                    TEAM B
     GPT-5.6                     GPT-1
 Architecture /              Runtime / Product /
 Governance /                 Implementation
 Decision Mgmt                  Management
          │                         │
          └────── Verification ────┘
```

**Operating principle:**

> تقسیم حوزه‌ها درشت است؛ مأموریت‌ها در داخل هر حوزه توسط Owner مدیریت می‌شوند.

> هیچ تصمیمی به‌خاطر تقسیم تیمی از PO عبور نمی‌کند.

---

**END — HBI-DUAL-TEAM-OPS-001 V1.0**
