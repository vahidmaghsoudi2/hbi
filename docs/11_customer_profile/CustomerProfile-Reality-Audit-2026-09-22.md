# HBI — Customer Profile 0→100 Reality Audit & Corrective Design

## تاریخ
31 شهریور 1405 / 2026-09-22

## Executive Decision
ممیزی Master نشان می‌دهد HBI امروز یک Customer Core ساده و مسیر فعال Customer→Case→Recommendation دارد، اما «پروفایل هوشمند تدریجی» هنوز به‌صورت مدل داده مستقل پیاده نشده است. پنج باکس UI قرارداد داده نهایی نیستند؛ فقط لایه نمایش روی قرارداد داده تثبیت‌شده خواهند بود.

**حکم:** قبل از UI بزرگ یا migration، قرارداد additive v1.1 لازم است. Recommendation، scoring، evidence و hard gates منجمد بمانند.

## 1. Reality Audit
### Customer
Customer فعلی شامل identity، consent پایه، age_range، sex_if_relevant، skin_profile، hair_profile، scalp_profile، concerns، observations، answers، case_history، operator_notes و timestamps است. چند فیلد پروفایل/یادداشت هنوز رشته‌ای و از نظر provenance/versioning ساختاریافته نیستند.

### Case
Case شامل customer_id، case_type، identified_needs، evidence_gaps، confidence، operator_override، reasoning_status و timestamps است.

### Intake/API
Quick Intake فعلاً name، mobile، concerns، consent، skin_profile، guest و open_case را می‌گیرد. وقتی open_case=true است، concerns و skin_profile به‌طور مستقیم روی Customer به‌عنوان پروفایل دائمی overwrite نمی‌شوند؛ recommendation_profile با concerns امروز ساخته می‌شود. این رفتار باید در قرارداد تثبیت شود.

### Recommendation
Recommendation به Case متصل است و integration test نشان می‌دهد profile شامل concerns و skin_profile به موتور می‌رسد. مسیر Customer→Case→Recommendation باید حفظ شود.

### Sale
Sale به Customer متصل است و خرید قابل بازیابی است؛ اما Purchase به‌تنهایی Preference یا Outcome نیست و Outcome مستقل فعلاً وجود ندارد.

### Structured profile concepts
Repository scan نشان می‌دهد مدل‌های مستقل ProfileFact / Preference / Outcome / Visit / ConsultationAnswer / Timeline برای این حوزه فعلاً وجود ندارند؛ اینها در اسناد به‌عنوان معماری هدف آمده‌اند.

## 2. چهار مأموریت
### Mission 1 — Reality / Reuse
**Reuse:** identity، consent پایه، age_range، skin/hair/scalp profile، concerns، Case، Sale، timestamps و recommendation_profile projection.

**احتیاط:** observations، answers، case_history و operator_notes به دلیل semantic/provenance ضعیف نباید بدون قرارداد جدید منبع Fact قطعی شوند.

### Mission 2 — Data Semantics
- Current Need = فقط scope همان Visit/Case.
- Profile Fact = ویژگی قابل اتکا با source/time/state.
- Preference = ترجیح مشتری؛ الزام ایمنی نیست.
- Constraint/Safety Signal = محدودیت/هشدار با source و severity.
- Product Interaction = viewed / recommended / purchased / used و مانند آن.
- Outcome = نتیجه یا بازخورد پس از تعامل.
- Derived Insight = projection، نه Fact.

**concerns نباید هم‌زمان Current Need و Permanent Fact باشد.**

### Mission 3 — Architecture / Red Team
نگاشت پنج باکس:
1. Need Today → Visit/Case
2. Skin/Hair Status → Profile Facts + current answers
3. Preferences/Constraints → Preference/Constraint
4. Key Product Experience → Product Interaction + Outcome
5. Smart Summary → derived projection

**رد معماری:** افزودن پنج ستون جدید به Customer. این کار semantic duplication و مشکل versioning ایجاد می‌کند.

### Mission 4 — PO Decision Pack
تصمیم‌های واقعی محصول:
1. MVP دقیق attributes پوست/مو.
2. vocabulary کنترل‌شده concerns و preferences.
3. freshness عملیاتی هر Fact.
4. مرز Safety Constraint در برابر Preference.
5. سیاست دسترسی/ویرایش مشتری و فروشنده.
6. ثبت Outcome در MVP یا بعد از Pilot.
7. consent برای دسته‌های داده حساس.

## 3. Existing → Action
| حوزه | واقعیت | اقدام |
|---|---|---|
| Identity | موجود | REUSE |
| Consent | binary فعلی | MODIFY later |
| concerns | رشته + ورودی Recommendation | REUSE now + constrain semantics |
| skin_profile | رشته | REUSE compatibility؛ structured future |
| hair/scalp | رشته | REUSE when relevant |
| Need Today | پخش بین concerns/Case | MODIFY به Visit scope |
| Preference | مدل مستقل ندارد | NEW |
| Constraint/Safety | مدل مستقل ندارد | NEW |
| Product experience | Purchase موجود | REUSE purchase؛ NEW interaction/outcome semantics |
| Outcome | ندارد | NEW |
| Fact | ندارد | NEW |
| Timeline | ندارد | NEW |
| Audit | domain audit ندارد | NEW |
| Smart Summary | ندارد | NEW as derived view |

## 4. Minimum Additive Model
برای Progressive Profiling، مدل حداقلی هدف:
- CustomerVisit / ConsultationSession
- ConsultationAnswer
- CustomerProfileFact
- CustomerPreference
- CustomerConstraint
- CustomerProductInteraction
- CustomerOutcome
- CustomerTimelineEvent
- CustomerDataAudit

همه نباید در یک migration بزرگ ساخته شوند.

Fact حداقل باید attribute_key، value، value_state، source، recorded_at، state و در صورت نیاز supersedes/validity داشته باشد.

Preference باید key/value/source/time و وضعیت تأیید داشته باشد.

Outcome باید interaction_id، outcome_type، customer_report، safety_flag، recorded_at و source داشته باشد.

## 5. UX Contract
Layer 1:
- Need Today
- Skin/Hair Status
- Preferences/Constraints
- Key Product Experience
- Smart Summary

Layer 2:
value + source + date + validity/state + history + edit/audit.

Layer 1 و Layer 2 دو دیتامدل نیستند؛ دو projection از داده معتبرند.

## 6. Progressive Profiling
1. Fact تازه و معتبر دوباره پرسیده نشود.
2. stale/conflict با برچسب نیازمند بررسی نمایش داده شود.
3. UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE از null و false متمایز باشند.
4. فقط سؤال مؤثر بر تصمیم فعلی پرسیده شود.
5. پاسخ همان جلسه بدون تأیید مشتری به Fact دائمی promotion نشود.

## 7. Smart Summary
Smart Summary باید generated/read-only و derived باشد، نه source-of-truth. باید قابل trace به records زیرین باشد و با تغییر آنها دوباره قابل تولید باشد.

## 8. Red-Team Findings
**Critical:** semantic overloading در Customer؛ نبود provenance/versioning واقعی؛ نبود Outcome مستقل؛ نبود Timeline/Audit دامنه پروفایل.

**Medium:** consent فعلی binary است؛ DTO عمومی فقط بخشی از profile را نشان می‌دهد؛ Case نزدیک‌ترین container فعلی به Visit است ولی جایگزین کامل آن نیست؛ search/get فعلاً snapshot هستند نه intelligence view.

**Good baselines:** Guest flow موجود است؛ ownership Case close در router فعلی بررسی می‌شود؛ integration test برای recommendation موجود است؛ اسناد promotion خودکار را ممنوع کرده‌اند.

## 9. Corrective Sequence
Gate A — Contract semantics/vocabulary.
Gate B — additive backend: Visit/Answer + Fact/Preference/Constraint حداقل.
Gate C — Audit/Timeline.
Gate D — read projection برای دو لایه UI.
Gate E — progressive questions پس از داده واقعی Pilot.
Gate F — recommendation adapter فقط read-only؛ scoring/gates تغییر نکند.

## 10. فعلاً ساخته نشود
پنج ستون دائمی روی Customer؛ Smart Summary ذخیره‌شده به‌عنوان Fact؛ promotion خودکار Purchase/Insight؛ پرسش‌نامه بلند؛ تصویر؛ segmentation/RFM/loyalty؛ تغییر Recommendation scoring/evidence gates.

## 11. Acceptance
**REALITY AUDIT = PASS WITH REQUIRED CONTRACT WORK**

این نتیجه به معنی آماده بودن برای کدنویسی UI نیست؛ به معنی تثبیت GAPهای واقعی و مسیر معماری است.

### Next controlled sequence
PO تصمیم‌های بخش 4 را تعیین کند → Contract/Dictionary v1.1 به‌روزرسانی شود → یک implementation slice کوچک انتخاب شود → تست و CI → سپس UI دو لایه.

## Evidence files audited
app/models/customer.py
app/models/case.py
app/api/routers/customers.py
app/api/routers/cases.py
app/services/customer_service.py
app/repositories/customer_repository.py
app/models/sale.py
tests/test_customer_profile_unit.py
tests/test_profile_consultation_recommendation_integration.py
docs/11_customer_profile/README.md
docs/11_customer_profile/CustomerProfile-v1-Implementation-Contract.md
docs/11_customer_profile/Data-Dictionary-v1.md
docs/11_customer_profile/Integration-Map.md
docs/11_customer_profile/Customer-Intelligence-Charter.md
docs/11_customer_profile/Editability-and-Versioning.md
docs/11_customer_profile/ROADMAP.md
