# HBI — رکوردهای کاری بانک مشکلات پوستی (S01 بسته؛ S02–S04 ثبت ساختاری؛ S05 در حال کار ساختاری)

**شناسه:** HBI-SKIN-PROBLEM-BANK-WORKING-RECORDS  
**ناوبری مرجع:** [فهرست عملیاتی](SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md) ← [مرجع تجمیعی](SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md) ← همین رکوردهای کاری؛ برای مرزهای ساختاری به [نقشهٔ پیش‌نویس (DRAFT / NOT THE ACTIVE PROBLEM BANK)](SKIN_PROBLEM_SPACE_MAP_V0.1.md) مراجعه کنید.  
**وضعیت:** **S01 STRUCTURALLY CLOSED; S02–S04 STRUCTURAL REGISTERED; S05 STRUCTURAL WORK IN PROGRESS** (2026-10-22) — S01 فقط از نظر مرز/ارجاع بسته است؛ S02 تا S04 ثبت ساختاری شده‌اند؛ S05 بستهٔ کاری ساختاری جاری است؛ **هیچ مورد جدیدی Accepted پزشکی/بانک نهایی نیست**  
**پوشه:** `docs/product-intake-knowledge-registry/` (فقط همین حوزه)  
**تاریخ تأییدهای PO (مرزها):** 2026-10-20  
**تاریخ بستن ساختاری پایلوت:** 2026-10-22  
**مالک تصمیم:** مقصودی (PO)  
**مبنای ساختاری:** `SKIN_PROBLEM_SPACE_MAP_V0.1.md` (master)  
**مراجع ادغام مرتبط:** PR #413، #414، #409 (merged)  
**محدودیت:** این سند Problem Bank V1 نهایی، Need، Product link، یا تأیید پزشکی نیست.

---

## S01 Pilot Closure — بستن ساختاری (نه پذیرش پزشکی)

**معنای Closure:** خوشهٔ S01 از نظر **ساختار، مرز، ارجاع و وضعیت کاری** قابل ارجاع و بسته است.  
**معنای غیر از Closure:** پذیرش پزشکی، بانک نهایی، Need، Ordinary-care قطعی، یا مجوز توصیهٔ محصول.

### جدول وضعیت نهایی پایلوت S01

| ID | نام کاری | نوع واحد (Map) | رابطه | پذیرش | عملیاتی | PO |
|----|----------|----------------|--------|--------|----------|-----|
| P01 | Dry skin / Xerosis | Problem / Clinical presentation | Primary | Scoped — Accepted=خیر | Deferred | confirmed |
| P02 | Dehydration / impaired moisture retention | Manifestation / related | Merge-candidate → Linked to P01 | Identified+Linked — Accepted=خیر | Undetermined | confirmed |
| P07 | Fissuring / cracking | Manifestation | Child/Related to P01 | Identified+Linked — Accepted=خیر | Undetermined | confirmed |
| P05 | Sensitive skin | Problem/presentation | Related مستقل هم‌قفسه | Identified/Scoped — Accepted=خیر | Undetermined | confirmed مرز |
| P06 | Irritant dermatitis | Clinical Condition; Clinical Anchor | S01→S05؛ متمایز از P01 | Identified — Accepted=خیر | Clinical-anchor only | ثبت ساختاری |

### آنچه عمداً خارج از این Closure است

| موضوع | وضعیت |
|--------|--------|
| G1 — فهرست پذیرفته‌شدهٔ ۶۲ موردی | **NOT RECOVERED** — خارج از دامنهٔ پایلوت S01؛ بازسازی ممنوع |
| G8 | **BLOCKED / NOT VERIFIED** |
| Need extraction | شروع نشده |
| Problem↔Product | شروع نشده |
| S03–S10 | در این بسته باز نشده‌اند؛ S03 صریحاً خارج از دامنه است |
| زبان مشتری / آستانه‌های ایمنی قطعی | عمدتاً UNKNOWN |

### قواعد قفل‌شده پس از Closure

1. تصمیم‌های PO برای P01/P02/P05/P07 بدون مدرک جدید و تأیید صریح PO تغییر نمی‌کنند.
2. P06 به خشکی ساده فروکاسته نمی‌شود.
3. Map placement ≠ medical validation ≠ Accepted.
4. S01 بستهٔ ساختاری است؛ S02 فقط پس از بازبینی و تأیید PO بسته می‌شود.

---

## تصمیم‌های تأییدشدهٔ PO (۲۰۲۶-۱۰-۲۰) — بدون تغییر

1. **P01:** تعریف فعلی با برچسب «پیشنهادی» برای بازبینی ساختاری پذیرفته شد؛ **نه پذیرش نهایی** (`Accepted` نیست).
2. **P02:** رکورد جداگانهٔ **Identified + Linked** باقی بماند؛ **ادغام یا حذف شناسه انجام نشود**.
3. **وضعیت عملیاتی P01:** فعلاً **Deferred** بماند تا `Ordinary-care candidate` بدون پشتوانهٔ کافی قطعی نشود.
4. **P07:** Identified + Linked به P01؛ ادغام نشود؛ Accepted نیست.
5. **P05:** Problem/presentation متمایز در S01؛ Related مستقل هم‌قفسه با P01؛ **ادغام با P01 ممنوع**؛ Accepted نیست؛ عملیاتی Undetermined؛ زبان مشتری و آستانهٔ ایمنی UNKNOWN مگر شاهد مخزن.
6. **محل نگهداری:** فقط `docs/product-intake-knowledge-registry/` — بدون انتقال یا تکثیر مرجع متعارف.

---

## قالب حداقلی رکورد (تثبیت‌شده برای پایلوت)

فیلدهای ضروری:

| فیلد | الزام |
|------|--------|
| ID نقشه | بله |
| نام کاری | بله |
| تعریف عملیاتی | بله |
| داخل دامنه | بله |
| خارج از دامنه | بله |
| نوع واحد | بله — Problem / Symptom-Manifestation / Clinical Anchor / Safety-Referral / Context-Descriptor |
| رابطه با نقشه | بله — Primary / Child / Related / Merge-candidate |
| وضعیت تکمیل و پذیرش | بله — Identified / Scoped / In review / Accepted / Deferred / Rejected |
| وضعیت عملیاتی | بله — Ordinary-care candidate / Clinical-anchor only / Safety-referral only / Out of scope / Deferred / Undetermined |
| ایمنی / ارجاع | بله |
| شواهد / منشأ | بله |
| زبان مشتری | بله — فقط شاهد واقعی؛ وگرنه UNKNOWN |
| UNKNOWN / GAP | بله |
| یادداشت بازبینی | اختیاری |

### قواعد

- چهار محور جدا می‌مانند: نوع واحد ≠ رابطه با نقشه ≠ وضعیت پذیرش ≠ وضعیت عملیاتی.
- زبان مشتری با پذیرش علمی/ساختاری گره نمی‌خورد.
- Child/Related ادغام خاموش نمی‌شود.
- خلأ با حدس پر نمی‌شود → `UNKNOWN`.
- نوشتن متن ≠ `Accepted`.
- Map placement ≠ medical validation ≠ Need ≠ Product authorization.

---

## رکورد P01 — Dry skin / Xerosis

| فیلد | محتوا |
|------|--------|
| ID نقشه | P01 |
| نام کاری | خشکی پوست / Dry skin (Xerosis) |
| تعریف عملیاتی | **پیشنهادی / نیازمند بازبینی ساختاری (تأیید PO برای ادامهٔ کار — نه Accepted).** نگرانی یا تظاهر encounter-relevant از خشکی سطح پوست در محدودهٔ مشاهدهٔ گالری؛ به‌خودی‌خود تشخیص بیماری نیست. |
| داخل دامنه | خشکی به‌عنوان Problem/Clinical presentation در S01 (طبق Map). |
| خارج از دامنه | ادغام با P05؛ فروکاستن P06 به خشکی ساده؛ تشخیص پزشکی؛ Need یا Product. |
| نوع واحد | Problem / Clinical presentation — **VERIFIED در Map** |
| رابطه با نقشه | Primary — **VERIFIED در Map** |
| وضعیت تکمیل و پذیرش | **Scoped** — **Accepted = خیر** (تصمیم PO) |
| وضعیت عملیاتی | **Deferred** (تصمیم PO) |
| ایمنی / ارجاع | **پیشنهاد احتیاطی / نیازمند بازبینی** — نه قاعدهٔ قطعی از Map. |
| شواهد / منشأ | Map V0.1 §S01 — P01 Mapped. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | زبان مشتری؛ شدت‌بندی؛ تمایز با درماتیت؛ فراوانی گالری؛ تعریف نهایی؛ آستانهٔ ایمنی |
| یادداشت بازبینی | تصمیم PO 2026-10-20. |

---

## رکورد P02 — Dehydration / impaired moisture retention

| فیلد | محتوا |
|------|--------|
| ID نقشه | P02 |
| نام کاری | Dehydration / impaired moisture retention |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** |
| داخل دامنه | رابطهٔ مرتبط/هم‌پوشان با P01 طبق Map. |
| خارج از دامنه | تعریف مستقل قطعی بدون شاهد؛ ادغام اجرایی؛ Need یا Product. |
| نوع واحد | Manifestation / related presentation — **VERIFIED در Map** |
| رابطه با نقشه | MERGE/RELATED TO P01 — Merge-candidate؛ ادغام اجرایی نشده |
| وضعیت تکمیل و پذیرش | **Identified + Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | Map V0.1 §4 و §6 (B01). |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف مستقل؛ مرز دقیق با P01؛ شمارش جدا؛ زبان مشتری |
| یادداشت بازبینی | تصمیم PO: Linked بماند؛ ادغام نشود. |

---

## رکورد P07 — Fissuring / cracking

| فیلد | محتوا |
|------|--------|
| ID نقشه | P07 |
| نام کاری | ترک / شکاف پوست (Fissuring / cracking) |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** |
| داخل دامنه | تظاهر مرتبط با P01 طبق Map. |
| خارج از دامنه | Need جدا؛ حذف شناسه؛ Product. |
| نوع واحد | Manifestation — **VERIFIED در Map** |
| رابطه با نقشه | Child / Related به P01 — **VERIFIED** |
| وضعیت تکمیل و پذیرش | **Identified + Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN / پیشنهاد احتیاطی نیازمند بازبینی** |
| شواهد / منشأ | Map V0.1 §S01 P07. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | شدت؛ مرز با زخم؛ زبان مشتری؛ آستانهٔ ارجاع |
| یادداشت بازبینی | تصمیم PO: Linked تأیید شد. |

---

## رکورد P05 — Sensitive skin

| فیلد | محتوا |
|------|--------|
| ID نقشه | P05 |
| نام کاری | پوست حساس (Sensitive skin) |
| تعریف عملیاتی | **UNKNOWN / تعریف پیشنهادی نیازمند بازبینی.** |
| داخل دامنه | Problem/presentation در S01 طبق Map. |
| خارج از دامنه | ادغام با P01؛ فرض حساسیت=خشکی؛ Need یا Product. |
| نوع واحد | Problem/presentation — **VERIFIED در Map** |
| رابطه با نقشه | Related مستقل هم‌قفسه با P01 — **PO-confirmed**؛ ادغام ممنوع |
| وضعیت تکمیل و پذیرش | **Identified / Scoped** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** (تصمیم PO) |
| ایمنی / ارجاع | **UNKNOWN** مگر شاهد مخزن |
| شواهد / منشأ | Map V0.1 §S01 P05؛ کامنت PO روی PR #413 |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ زبان مشتری؛ وضعیت عملیاتی؛ آستانهٔ ایمنی |
| یادداشت بازبینی | تصمیم PO 2026-10-20: متمایز بماند؛ ادغام با P01 نشود. |

---

## رکورد P06 — Irritant dermatitis

| فیلد | محتوا |
|------|--------|
| ID نقشه | P06 |
| نام کاری | درماتیت تحریکی (Irritant dermatitis) |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map تعریف عملیاتی تفصیلی ارائه نمی‌کند؛ این خلأ به‌عنوان UNKNOWN حفظ می‌شود. |
| داخل دامنه | Clinical Condition / inflammatory presentation با مسیر ساختاری S01→S05، مطابق Map. |
| خارج از دامنه | فروکاستن به خشکی سادهٔ P01؛ تلقی به‌عنوان Need پذیرفته‌شده؛ Ordinary-care candidate یا مجوز درمان. |
| نوع واحد | Clinical Condition / inflammatory presentation — **VERIFIED در Map**؛ Clinical Anchor |
| رابطه با نقشه | S01→S05 Clinical Anchor — طبق Map؛ از P01 متمایز می‌ماند و به خشکی ساده فروکاسته نمی‌شود. |
| وضعیت تکمیل و پذیرش | **Identified** — ثبت ساختاری؛ **Accepted = خیر**. این ثبت به‌خودی‌خود تأیید PO یا اعتبارسنجی پزشکی نیست. |
| وضعیت عملیاتی | **Clinical-anchor only** — نه Ordinary-care candidate. |
| ایمنی / ارجاع | **UNKNOWN** — Map برای P06 آستانهٔ اختصاصی ایمنی/ارجاع تعیین نکرده است. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4، بخش S01: `P06 Irritant dermatitis — Clinical Condition/inflammatory presentation — S01→S05 — Clinical Anchor`. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ زبان مشتری؛ رابطهٔ عملیاتی دقیق با فرایند گالری؛ آستانهٔ ایمنی/ارجاع؛ شواهد بالینی مستقل |
| یادداشت بازبینی | ثبت ساختاری P06 بر اساس Map؛ هیچ وضعیت Accepted یا Ordinary-care برای آن ادعا نمی‌شود. |

---

## S02 — Oil / Sebum / Follicular Balance (ثبت ساختاری؛ نه Accepted)

### جدول خلاصهٔ S02

| ID | نام Map | نوع واحد | رابطه با Map | پذیرش | عملیاتی | UNKNOWNهای اصلی |
|----|---------|----------|--------------|--------|----------|-----------------|
| P03 | Oily skin / Seborrhoea | Problem / presentation — VERIFIED در Map | S02 — Mapped؛ رابطهٔ اختصاصی با Pهای دیگر UNKNOWN | Identified — Accepted=خیر | Undetermined | تعریف عملیاتی؛ مرز oiliness/seborrhoea؛ روابط دیگر؛ ایمنی/ارجاع؛ زبان مشتری |
| P04 | Combination skin | State Descriptor — VERIFIED در Map | S02 — Descriptor؛ صریحاً «نه Problem مستقل»؛ رابطهٔ بیشتر UNKNOWN | Identified — Accepted=خیر | Undetermined | تعریف توصیفی دقیق؛ نسبت با P03؛ زبان مشتری؛ ایمنی/ارجاع؛ اینکه در مدل کاری چه استفادهٔ مجازی دارد |

### رکورد P03 — Oily skin / Seborrhoea

| فیلد | محتوا |
|------|--------|
| ID نقشه | P03 |
| نام کاری | چربی پوست / Oily skin / Seborrhoea |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی ساختاری.** Map نام و جایگاه را ثبت می‌کند اما تعریف عملیاتی تفصیلی ارائه نمی‌کند. |
| داخل دامنه | Problem/presentation در قفسهٔ S02 — Oil / Sebum / Follicular Balance، مطابق Map V0.1 §2 و §4. |
| خارج از دامنه | تشخیص پزشکی؛ ادعای رابطه با Pهای دیگر بدون ذکر صریح Map؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | Problem / presentation — **VERIFIED در Map** |
| رابطه با نقشه | S02 — Mapped؛ رابطهٔ اختصاصی با سایر Pها در Map برای P03 ذکر نشده: **UNKNOWN** |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §2 (S02) و §4 (S02: P03 Oily skin/Seborrhoea — Problem/presentation — S02 — Mapped). |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ مرز میان oiliness و seborrhoea؛ رابطهٔ دقیق با P04 یا سایر Pها؛ زبان مشتری؛ ایمنی/ارجاع؛ تناسب عملیاتی HBI. |
| یادداشت بازبینی | ثبت ساختاری از Map؛ هیچ پذیرش پزشکی یا Need/‌Product استنباط نشده است. |

### رکورد P04 — Combination skin

| فیلد | محتوا |
|------|--------|
| ID نقشه | P04 |
| نام کاری | پوست مختلط / Combination skin |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی ساختاری.** Map آن را State Descriptor می‌نامد و تصریح می‌کند که به‌طور خودکار Problem مستقل نیست؛ تعریف عملیاتی دقیق ارائه نشده است. |
| داخل دامنه | ثبت به‌عنوان State Descriptor در قفسهٔ S02، با حفظ قید «Descriptor, not independent Problem». |
| خارج از دامنه | تبدیل خودکار به Problem مستقل؛ فرض رابطهٔ قطعی با P03؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | **State Descriptor — VERIFIED در Map** |
| رابطه با نقشه | S02 — Descriptor, not independent Problem؛ رابطهٔ صریح‌تر با P03 یا سایر Pها: **UNKNOWN** |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §2 (S02: Combination skin is not automatically an independent Problem) و §4 (P04 State Descriptor — S02 — Descriptor, not independent Problem). |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف توصیفی دقیق؛ رابطه با P03؛ زبان مشتری؛ ایمنی/ارجاع؛ اینکه آیا و چگونه این descriptor در کارکردهای بعدی مجاز است. |
| یادداشت بازبینی | ثبت ساختاری به‌عنوان descriptor؛ به‌عنوان Problem مستقل یا Need پذیرفته نشده است. |

### روابط خوشهٔ S02

| ID | رابطهٔ صریح در Map | وضعیت ثبت کاری |
|----|--------------------|-----------------|
| P03 | S02 — Mapped | Problem/presentation؛ رابطهٔ بیشتر UNKNOWN |
| P04 | S02 — State Descriptor؛ not independent Problem | Descriptor؛ رابطهٔ بیشتر UNKNOWN |

هیچ رابطهٔ P03↔P04 به‌صورت قطعی در Map تصریح نشده؛ بنابراین ارتباط مستقیم میان آن‌ها **UNKNOWN** است. این بخش هیچ ادغام یا پیوند تازه‌ای را ایجاد نمی‌کند.

---

## S03 — Acne / Follicular / Pore Presentation (در حال کار ساختاری؛ نه Accepted)

### جدول خلاصهٔ S03

| ID | نام Map | نوع واحد | رابطه با Map | پذیرش | عملیاتی | UNKNOWNهای اصلی |
|----|---------|----------|--------------|--------|----------|-----------------|
| P08 | Acne | Problem / Clinical presentation | S03 — Mapped; parent of P09–P12; relation to P13 is Cross-Shelf only as mapped | Identified — Accepted=خیر | Undetermined | تعریف عملیاتی؛ دامنه و مرز؛ زبان مشتری؛ ایمنی/ارجاع؛ تناسب عملیاتی HBI |
| P09 | Blackheads/open comedones | Manifestation/subtype | Child/Related to P08 — Linked; not merged | Identified+Linked — Accepted=خیر | Undetermined | تعریف عملیاتی؛ رابطهٔ دقیق subtype؛ زبان مشتری؛ ایمنی/ارجاع |
| P10 | Whiteheads/closed comedones | Manifestation/subtype | Child/Related to P08 — Linked; not merged | Identified+Linked — Accepted=خیر | Undetermined | تعریف عملیاتی؛ رابطهٔ دقیق subtype؛ زبان مشتری؛ ایمنی/ارجاع |
| P11 | Inflammatory acne lesions | Manifestation/subtype | Child/Related to P08 — Linked; not merged | Identified+Linked — Accepted=خیر | Undetermined | تعریف عملیاتی؛ مرز subtype؛ زبان مشتری؛ ایمنی/ارجاع |
| P12 | Nodular/cystic acne | Severity/clinical subtype | P08 — Clinical/Severity Anchor | Identified+Linked — Accepted=خیر | Clinical-anchor only | تعریف عملیاتی؛ مرز شدت/لنگر بالینی؛ زبان مشتری؛ ایمنی/ارجاع |
| P13 | Acne aftermath/discoloration | Sequela/post-inflammatory presentation | P08→S04 — Related/Cross-Shelf; relation recorded only, S04 not opened | Identified+Linked — Accepted=خیر | Undetermined | مرز با S04؛ تعریف دقیق؛ زبان مشتری؛ ایمنی/ارجاع |
| P14 | Folliculitis | Clinical Condition/follicular presentation | S03 — Clinical Anchor; HBI relevance unresolved | Identified — Accepted=خیر | Clinical-anchor only | HBI relevance unresolved؛ تعریف عملیاتی؛ زبان مشتری؛ ایمنی/ارجاع |
| P15 | Pseudofolliculitis/razor bumps | Problem/follicular presentation | S03 — Mapped | Identified — Accepted=خیر | Undetermined | تعریف عملیاتی؛ مرز با P14؛ زبان مشتری؛ ایمنی/ارجاع |
| P16 | Sebaceous hyperplasia | Clinical Condition/lesion presentation | Map lists in S03 text block, but path is S02→S07 — Clinical Anchor; HBI relevance unresolved | Identified — Accepted=خیر | Clinical-anchor only | Map shelf/path discrepancy; HBI relevance unresolved; definition; language; safety/referral |

### رکورد P08 — Acne

| فیلد | محتوا |
|------|--------|
| ID نقشه | P08 |
| نام کاری | آکنه / Acne |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی ساختاری.** Map نام و جایگاه را ثبت می‌کند؛ تعریف عملیاتی تفصیلی در Map ارائه نشده است. |
| داخل دامنه | Problem/Clinical presentation در S03 طبق Map V0.1 §4. |
| خارج از دامنه | تشخیص پزشکی؛ تعریف بالینی افزوده؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | Problem / Clinical presentation — **VERIFIED در Map** |
| رابطه با نقشه | S03 — Mapped؛ والد ساختاری P09–P12 طبق Map/Boundary Register؛ رابطهٔ P13 فقط Cross-Shelf به S04 طبق Map. |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** — آستانهٔ اختصاصی از این Map استنتاج نمی‌شود. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §6 B02. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ granularity نهایی؛ زبان مشتری؛ ایمنی/ارجاع؛ تناسب عملیاتی HBI. |
| یادداشت بازبینی | فقط ثبت ساختاری؛ Map placement ≠ medical validation ≠ Need acceptance. |

### رکورد P09 — Blackheads / open comedones

| فیلد | محتوا |
|------|--------|
| ID نقشه | P09 |
| نام کاری | Blackheads / open comedones |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** فقط نوع و رابطهٔ Map ثبت می‌شود. |
| داخل دامنه | Manifestation/subtype مرتبط با P08 طبق Map. |
| خارج از دامنه | تبدیل به Problem مستقل یا Need؛ ادغام یا حذف شناسه؛ تعریف پزشکی افزوده. |
| نوع واحد | Manifestation/subtype — **VERIFIED در Map** |
| رابطه با نقشه | Child/Related to P08 — **Identified+Linked**؛ مستقل‌سازی یا ادغام انجام نشده است. |
| وضعیت تکمیل و پذیرش | **Identified+Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §6 B02. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ جزئیات رابطه با P08؛ زبان مشتری؛ ایمنی/ارجاع. |
| یادداشت بازبینی | شناسه حفظ شده؛ Child/Related به معنای ادغام نیست. |

### رکورد P10 — Whiteheads / closed comedones

| فیلد | محتوا |
|------|--------|
| ID نقشه | P10 |
| نام کاری | Whiteheads / closed comedones |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** فقط نوع و رابطهٔ Map ثبت می‌شود. |
| داخل دامنه | Manifestation/subtype مرتبط با P08 طبق Map. |
| خارج از دامنه | تبدیل به Problem مستقل یا Need؛ ادغام یا حذف شناسه؛ تعریف پزشکی افزوده. |
| نوع واحد | Manifestation/subtype — **VERIFIED در Map** |
| رابطه با نقشه | Child/Related to P08 — **Identified+Linked**؛ مستقل‌سازی یا ادغام انجام نشده است. |
| وضعیت تکمیل و پذیرش | **Identified+Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §6 B02. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ جزئیات رابطه با P08؛ زبان مشتری؛ ایمنی/ارجاع. |
| یادداشت بازبینی | شناسه حفظ شده؛ Child/Related به معنای ادغام نیست. |

### رکورد P11 — Inflammatory acne lesions

| فیلد | محتوا |
|------|--------|
| ID نقشه | P11 |
| نام کاری | Inflammatory acne lesions |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** فقط نوع و رابطهٔ Map ثبت می‌شود. |
| داخل دامنه | Manifestation/subtype مرتبط با P08 طبق Map. |
| خارج از دامنه | تبدیل به Problem مستقل یا Need؛ ادغام یا حذف شناسه؛ تعریف پزشکی افزوده. |
| نوع واحد | Manifestation/subtype — **VERIFIED در Map** |
| رابطه با نقشه | Child/Related to P08 — **Identified+Linked**؛ مستقل‌سازی یا ادغام انجام نشده است. |
| وضعیت تکمیل و پذیرش | **Identified+Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §6 B02. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ مرز دقیق subtype؛ زبان مشتری؛ ایمنی/ارجاع. |
| یادداشت بازبینی | شناسه حفظ شده؛ Child/Related به معنای ادغام نیست. |

### رکورد P12 — Nodular / cystic acne

| فیلد | محتوا |
|------|--------|
| ID نقشه | P12 |
| نام کاری | Nodular / cystic acne |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map آن را Severity/clinical subtype و Clinical/Severity Anchor می‌نامد؛ تعریف تفصیلی افزوده نمی‌شود. |
| داخل دامنه | Severity/clinical subtype مرتبط با P08 طبق Map. |
| خارج از دامنه | تبدیل به Ordinary-care candidate؛ تعریف شدت پزشکی؛ Need؛ Product؛ درمان یا تشخیص. |
| نوع واحد | Severity/clinical subtype — **VERIFIED در Map**؛ Clinical/Severity Anchor |
| رابطه با نقشه | P08 — Clinical/Severity Anchor؛ شناسه مستقل حفظ می‌شود. |
| وضعیت تکمیل و پذیرش | **Identified+Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Clinical-anchor only** |
| ایمنی / ارجاع | **UNKNOWN** — این ثبت به‌تنهایی آستانه یا پروتکل ارجاع تعریف نمی‌کند. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §6 B02. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ مرز شدت؛ زبان مشتری؛ ایمنی/ارجاع؛ رابطهٔ دقیق با گیت‌های عملیاتی HBI. |
| یادداشت بازبینی | Clinical/Severity Anchor طبق Map؛ Ordinary-care صریحاً تعیین نشده است. |

### رکورد P13 — Acne aftermath / discoloration

| فیلد | محتوا |
|------|--------|
| ID نقشه | P13 |
| نام کاری | Acne aftermath / discoloration |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map آن را Sequela/post-inflammatory presentation و Cross-Shelf معرفی می‌کند؛ تعریف افزوده نمی‌شود. |
| داخل دامنه | ثبت رابطهٔ P08→S04 به‌عنوان Related/Cross-Shelf؛ فقط رابطه ثبت می‌شود. |
| خارج از دامنه | بازکردن یا تکمیل S04؛ تکمیل موضوع رنگ‌دانه؛ تعریف بالینی؛ Need؛ Product. |
| نوع واحد | Sequela/post-inflammatory presentation — **VERIFIED در Map** |
| رابطه با نقشه | P08→S04 — Related/Cross-Shelf؛ بدون بازکردن S04. |
| وضعیت تکمیل و پذیرش | **Identified+Linked** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03 و §5 Cross-Shelf Relationships. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف و مرز دقیق؛ مقصد/مفهوم S04 خارج از این بسته؛ زبان مشتری؛ ایمنی/ارجاع. |
| یادداشت بازبینی | رابطهٔ Cross-Shelf فقط ثبت شد؛ S04 شروع نشده است. |

### رکورد P14 — Folliculitis

| فیلد | محتوا |
|------|--------|
| ID نقشه | P14 |
| نام کاری | Folliculitis |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map فقط نوع و جایگاه ساختاری را تعیین می‌کند. |
| داخل دامنه | Clinical Condition/follicular presentation؛ Clinical Anchor در S03 طبق Map. |
| خارج از دامنه | تعریف تشخیصی افزوده؛ فرض تناسب HBI؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | Clinical Condition/follicular presentation — **VERIFIED در Map**؛ Clinical Anchor |
| رابطه با نقشه | S03 — Clinical Anchor؛ **HBI relevance unresolved**. |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Clinical-anchor only** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | HBI relevance unresolved؛ تعریف عملیاتی؛ زبان مشتری؛ ایمنی/ارجاع؛ شواهد اختصاصی. |
| یادداشت بازبینی | Anchor ثبت شده؛ HBI relevance حل نشده است. |

### رکورد P15 — Pseudofolliculitis / razor bumps

| فیلد | محتوا |
|------|--------|
| ID نقشه | P15 |
| نام کاری | Pseudofolliculitis / razor bumps |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map نام و جایگاه را ثبت می‌کند؛ تعریف تفصیلی افزوده نمی‌شود. |
| داخل دامنه | Problem/follicular presentation در S03 طبق Map. |
| خارج از دامنه | فرض هم‌ارزی با P14؛ تعریف پزشکی افزوده؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | Problem/follicular presentation — **VERIFIED در Map** |
| رابطه با نقشه | S03 — Mapped؛ رابطهٔ صریح با P14 در Map مشخص نشده: **UNKNOWN**. |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Undetermined** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S03. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | تعریف عملیاتی؛ رابطه با P14؛ زبان مشتری؛ ایمنی/ارجاع؛ تناسب عملیاتی HBI. |
| یادداشت بازبینی | مستقل از P14 نگه داشته شد؛ هیچ رابطهٔ جدیدی استنباط نشده است. |

### رکورد P16 — Sebaceous hyperplasia

| فیلد | محتوا |
|------|--------|
| ID نقشه | P16 |
| نام کاری | Sebaceous hyperplasia |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map فقط Clinical Condition/lesion presentation و جایگاه/مسیر را ثبت می‌کند. |
| داخل دامنه | ثبت در این بسته طبق دستور PO؛ Map آن را در بلوک متنی S03 آورده، اما مسیر صریح آن **S02→S07** است. |
| خارج از دامنه | انتقال به S03 بدون پشتوانه؛ تغییر مسیر S02→S07؛ بازکردن S02/S07؛ تعریف پزشکی؛ Need؛ Product. |
| نوع واحد | Clinical Condition/lesion presentation — **VERIFIED در Map**؛ Clinical Anchor |
| رابطه با نقشه | مسیر Map: **S02→S07** — Clinical Anchor؛ **HBI relevance unresolved**. قرارگیری در بلوک متنی S03 با مسیر صریح Map متفاوت است؛ تعارض/ابهام حفظ می‌شود. |
| وضعیت تکمیل و پذیرش | **Identified** — **Accepted = خیر** |
| وضعیت عملیاتی | **Clinical-anchor only** |
| ایمنی / ارجاع | **UNKNOWN** |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4، خط P16 در بلوک S03؛ مسیر صریح S02→S07. |
| زبان مشتری | **UNKNOWN** |
| UNKNOWN / GAP | اختلاف بلوک متنی/مسیر قفسه؛ HBI relevance unresolved؛ تعریف عملیاتی؛ زبان مشتری؛ ایمنی/ارجاع. |
| یادداشت بازبینی | در بستهٔ اجرایی S03 ثبت شده چون دستور PO صریحاً خواسته؛ مسیر Map تغییر داده نشده و P16 به S02 بازگردانده نشده است. |

### روابط خوشهٔ S03 (بدون ادغام خاموش)

| ID | رابطهٔ صریح در Map | وضعیت ثبت کاری |
|----|--------------------|-----------------|
| P08 | S03 — Mapped; parent context for P09–P12 per Map/Boundary Register | Problem/Clinical presentation؛ والد ساختاری |
| P09 | Child/Related to P08 | Identified+Linked؛ شناسه حفظ شده |
| P10 | Child/Related to P08 | Identified+Linked؛ شناسه حفظ شده |
| P11 | Child/Related to P08 | Identified+Linked؛ شناسه حفظ شده |
| P12 | P08 — Clinical/Severity Anchor | Identified+Linked؛ Clinical-anchor only |
| P13 | P08→S04 — Related/Cross-Shelf | فقط رابطه ثبت شد؛ S04 باز نشده |
| P14 | S03 — Clinical Anchor/HBI relevance unresolved | Clinical-anchor only؛ relevance unresolved |
| P15 | S03 — Mapped | رابطهٔ خاص با P14 UNKNOWN |
| P16 | Map path S02→S07; Clinical Anchor/HBI relevance unresolved | در این بسته طبق دستور؛ مسیر Map تغییر نکرده |

هیچ ادغام یا حذف شناسه انجام نشده است. روابطی که Map صریحاً مشخص نکرده، **UNKNOWN** باقی می‌مانند.

---


## S04 — Pigmentation / Color (در حال کار ساختاری؛ نه Accepted)

### جدول خلاصهٔ S04

| ID | نام Map | نوع واحد | رابطه با Map | پذیرش | عملیاتی | UNKNOWNهای اصلی |
|----|---------|----------|--------------|--------|----------|-----------------|
| P17 | Hyperpigmentation / dark spots | Problem/presentation — VERIFIED در Map | S04 — Mapped؛ والد ساختاری P18/P19 در حد Map | Identified — Accepted=خیر | Undetermined | تعریف عملیاتی؛ مرز خانواده؛ زبان مشتری؛ شواهد/ایمنی |
| P18 | Melasma | Clinical Condition — VERIFIED در Map | P17/S04 — Clinical Anchor؛ Linked به P17 در حد Map | Identified+Linked — Accepted=خیر | Clinical-anchor only | تعریف عملیاتی؛ HBI relevance؛ زبان مشتری؛ شواهد/ارجاع |
| P19 | Post-inflammatory hyperpigmentation | Sequela/pigmentation presentation — VERIFIED در Map | P17/S04 — Related/Sequela؛ Linked به P17؛ ادغام نشده | Identified+Linked — Accepted=خیر | Undetermined | تعریف/مرز؛ رابطهٔ دقیق با P17؛ زبان مشتری؛ شواهد |
| P20 | Hypopigmentation | Problem/presentation — VERIFIED در Map | S04 — Mapped؛ evidence boundary retained | Identified — Accepted=خیر | Undetermined | evidence boundary؛ تعریف عملیاتی؛ زبان مشتری؛ شواهد مستقل |
| P21 | Vitiligo | Clinical Condition — VERIFIED در Map | S04 — Clinical/Referral-sensitive | Identified — Accepted=خیر | Clinical-anchor only | مرز referral؛ HBI relevance؛ تعریف/شواهد؛ زبان مشتری |
| P22 | Sun-related pigmentation | Context/pigmentation presentation — VERIFIED در Map | P17/S09 — Related/Context؛ S09 صرفاً مرجع رابطه | Identified+Linked — Accepted=خیر | Undetermined | مرز Context با Problem؛ رابطهٔ دقیق؛ زبان مشتری؛ شواهد |
| P23 | Poikiloderma | Clinical Condition/UV-associated presentation — VERIFIED در Map | S04↔S09 — Parked/Evidence Boundary | Deferred — Accepted=خیر | Undetermined | evidence boundary؛ دلیل/معیار بازگشایی؛ HBI relevance؛ زبان مشتری |
| P13 | Acne aftermath/discoloration (ارجاع از S03) | Sequela/post-inflammatory presentation | P08→S04 — Related/Cross-Shelf؛ رکورد S03 موجود است | بدون تغییر در این بسته | بدون تغییر در این بسته | فقط ارجاع مرزی؛ S03 بازنویسی نشده |

### رکورد P17 — Hyperpigmentation / dark spots

| فیلد | محتوا |
|------|--------|
| ID نقشه | P17 |
| نام کاری | Hyperpigmentation / dark spots |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی ساختاری.** فقط جایگاه Problem/presentation از Map ثبت می‌شود. |
| داخل دامنه | Problem/presentation در S04 طبق Map V0.1 §4. |
| خارج از دامنه | تشخیص پزشکی؛ تعریف یا زیرگروه افزوده؛ Need؛ Product؛ توصیه یا درمان. |
| نوع واحد | Problem/presentation — VERIFIED در Map |
| رابطه با نقشه | S04 — Mapped؛ والد ساختاری P18/P19 فقط در حد Map؛ ادغام ممنوع. |
| وضعیت تکمیل و پذیرش | Identified — Accepted = خیر |
| وضعیت عملیاتی | Undetermined |
| ایمنی / ارجاع | UNKNOWN |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04؛ §6 B03. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | تعریف عملیاتی؛ مرز خانواده؛ زبان مشتری؛ شواهد مستقل؛ آستانهٔ ایمنی/ارجاع. |
| یادداشت بازبینی | ثبت ساختاری؛ Map placement ≠ medical validation ≠ Accepted. |

### رکورد P18 — Melasma

| فیلد | محتوا |
|------|--------|
| ID نقشه | P18 |
| نام کاری | Melasma |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map نوع Clinical Condition و جایگاه Clinical Anchor را تعیین می‌کند؛ تعریف تفصیلی افزوده نمی‌شود. |
| داخل دامنه | Clinical Condition مرتبط با P17/S04 طبق Map. |
| خارج از دامنه | تشخیص؛ تعریف بالینی افزوده؛ Ordinary-care؛ Need؛ Product؛ درمان. |
| نوع واحد | Clinical Condition — VERIFIED در Map؛ Clinical Anchor |
| رابطه با نقشه | P17/S04 — Clinical Anchor؛ Linked به P17 فقط در حد رابطهٔ Map. |
| وضعیت تکمیل و پذیرش | Identified+Linked — Accepted = خیر |
| وضعیت عملیاتی | Clinical-anchor only |
| ایمنی / ارجاع | UNKNOWN؛ جزئیات referral از Map استنتاج نمی‌شود. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | تعریف عملیاتی؛ HBI relevance؛ زبان مشتری؛ شواهد مستقل؛ مرز/آستانهٔ ارجاع. |
| یادداشت بازبینی | Clinical Anchor است؛ Ordinary-care candidate نیست. |

### رکورد P19 — Post-inflammatory hyperpigmentation

| فیلد | محتوا |
|------|--------|
| ID نقشه | P19 |
| نام کاری | Post-inflammatory hyperpigmentation |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map آن را Sequela/pigmentation presentation معرفی می‌کند؛ تعریف افزوده نمی‌شود. |
| داخل دامنه | Sequela مرتبط با P17/S04 طبق Map. |
| خارج از دامنه | ادغام با P17؛ تعریف پزشکی افزوده؛ Need؛ Product؛ درمان. |
| نوع واحد | Sequela/pigmentation presentation — VERIFIED در Map |
| رابطه با نقشه | P17/S04 — Related/Sequela؛ Identified+Linked؛ شناسه حفظ می‌شود و ادغام نمی‌شود. |
| وضعیت تکمیل و پذیرش | Identified+Linked — Accepted = خیر |
| وضعیت عملیاتی | Undetermined |
| ایمنی / ارجاع | UNKNOWN |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04 و §6 B03. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | تعریف و مرز دقیق؛ رابطهٔ دقیق با P17؛ زبان مشتری؛ شواهد مستقل؛ ایمنی/ارجاع. |
| یادداشت بازبینی | Sequela/Related باقی می‌ماند؛ به Problem مستقل یا Accepted تبدیل نشده است. |

### رکورد P20 — Hypopigmentation

| فیلد | محتوا |
|------|--------|
| ID نقشه | P20 |
| نام کاری | Hypopigmentation |
| تعریف عملیاتی | **UNKNOWN / evidence boundary retained.** Map جایگاه Problem/presentation را می‌دهد؛ مرز شواهد باید حفظ شود. |
| داخل دامنه | Problem/presentation در S04 طبق Map، با حفظ evidence boundary. |
| خارج از دامنه | ادعای شواهد/سبب‌شناسی بدون منبع؛ ادغام با P21؛ Need؛ Product؛ درمان. |
| نوع واحد | Problem/presentation — VERIFIED در Map |
| رابطه با نقشه | S04 — Mapped; evidence boundary retained. |
| وضعیت تکمیل و پذیرش | Identified — Accepted = خیر |
| وضعیت عملیاتی | Undetermined |
| ایمنی / ارجاع | UNKNOWN |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | **Evidence boundary retained**؛ تعریف عملیاتی؛ شواهد مستقل؛ زبان مشتری؛ رابطه با P21 نامذکور و UNKNOWN. |
| یادداشت بازبینی | هیچ توضیح یا رابطهٔ بالینی خارج از Map ساخته نشده است. |

### رکورد P21 — Vitiligo

| فیلد | محتوا |
|------|--------|
| ID نقشه | P21 |
| نام کاری | Vitiligo |
| تعریف عملیاتی | **UNKNOWN / نیازمند بازبینی.** Map آن را Clinical Condition و Clinical/Referral-sensitive مشخص می‌کند؛ تعریف افزوده نمی‌شود. |
| داخل دامنه | Clinical Condition در S04 طبق Map، با حفظ حساسیت ارجاع. |
| خارج از دامنه | Ordinary-care؛ تشخیص؛ تعریف پزشکی افزوده؛ Need؛ Product؛ درمان. |
| نوع واحد | Clinical Condition — VERIFIED در Map؛ Clinical/Referral-sensitive |
| رابطه با نقشه | S04 — Clinical/Referral-sensitive. |
| وضعیت تکمیل و پذیرش | Identified — Accepted = خیر |
| وضعیت عملیاتی | Clinical-anchor only |
| ایمنی / ارجاع | Referral-sensitive طبق Map؛ جزئیات آستانه/پروتکل UNKNOWN. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | تعریف عملیاتی؛ مرز referral؛ HBI relevance؛ زبان مشتری؛ شواهد/آستانه‌های ارجاع. |
| یادداشت بازبینی | Clinical/Referral-sensitive؛ Ordinary-care نیست و Accepted نشده است. |

### رکورد P22 — Sun-related pigmentation

| فیلد | محتوا |
|------|--------|
| ID نقشه | P22 |
| نام کاری | Sun-related pigmentation |
| تعریف عملیاتی | **UNKNOWN / Context only as mapped.** Map جایگاه Context/pigmentation presentation را تعیین می‌کند. |
| داخل دامنه | رابطهٔ Context در P17/S09؛ فقط ثبت مرز و ارجاع ساختاری. |
| خارج از دامنه | تبدیل Context به Problem مستقل/Need؛ بازکردن یا تکمیل S09؛ ادعای علیت یا درمان. |
| نوع واحد | Context/pigmentation presentation — VERIFIED در Map |
| رابطه با نقشه | P17/S09 — Related/Context؛ رابطهٔ S09 ثبت می‌شود اما S09 باز نمی‌شود. |
| وضعیت تکمیل و پذیرش | Identified+Linked — Accepted = خیر |
| وضعیت عملیاتی | Undetermined |
| ایمنی / ارجاع | UNKNOWN |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04 و §5 Cross-Shelf Relationships. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | مرز Context با Problem؛ رابطهٔ دقیق با P17؛ جزئیات S09 خارج از دامنه؛ زبان مشتری؛ شواهد. |
| یادداشت بازبینی | Context ≠ Accepted Problem/Need؛ S09 باز نشده است. |

### رکورد P23 — Poikiloderma

| فیلد | محتوا |
|------|--------|
| ID نقشه | P23 |
| نام کاری | Poikiloderma |
| تعریف عملیاتی | **UNKNOWN / Parked — Evidence Boundary.** هیچ تعریف یا ادعای شواهدی فراتر از Map افزوده نمی‌شود. |
| داخل دامنه | ثبت وضعیت Parked/Evidence Boundary و رابطهٔ S04↔S09 طبق Map. |
| خارج از دامنه | تکمیل بالینی؛ ادعای شواهد؛ بازکردن S09؛ Need؛ Product؛ تبدیل به Ordinary-care. |
| نوع واحد | Clinical Condition/UV-associated presentation — VERIFIED در Map |
| رابطه با نقشه | S04↔S09 — Parked/Evidence Boundary؛ S09 باز نمی‌شود. |
| وضعیت تکمیل و پذیرش | Deferred — Accepted = خیر |
| وضعیت عملیاتی | Undetermined |
| ایمنی / ارجاع | UNKNOWN؛ هیچ آستانه‌ای از Map استنتاج نمی‌شود. |
| شواهد / منشأ | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S04. |
| زبان مشتری | UNKNOWN |
| UNKNOWN / GAP | Evidence boundary؛ معیار/شرط بازگشایی؛ HBI relevance؛ زبان مشتری؛ شواهد مستقل. |
| یادداشت بازبینی | Parked/Deferred؛ نه Accepted و نه Ordinary-care. |

### روابط S04 (بدون ادغام خاموش)

| ID | رابطهٔ صریح در Map | وضعیت ثبت کاری |
|----|--------------------|-----------------|
| P17 | S04 — Mapped | Problem/presentation؛ والد ساختاری P18/P19 در حد Map |
| P18 | P17/S04 — Clinical Anchor | Identified+Linked؛ Clinical-anchor only |
| P19 | P17/S04 — Related/Sequela | Identified+Linked؛ شناسه حفظ شده؛ ادغام نشده |
| P20 | S04 — Mapped; evidence boundary retained | Identified؛ boundary در UNKNOWN/GAP حفظ شد |
| P21 | S04 — Clinical/Referral-sensitive | Identified؛ Clinical-anchor only؛ آستانهٔ referral UNKNOWN |
| P22 | P17/S09 — Related/Context | Context ثبت شد؛ S09 باز نشده |
| P23 | S04↔S09 — Parked/Evidence Boundary | Deferred؛ S09 باز نشده |
| P13 | P08→S04 — Related/Cross-Shelf | فقط ارجاع؛ رکورد S03 بدون تغییر |

هیچ رابطه‌ای فراتر از Map استنباط نشده است. P17 با P18/P19 ادغام نشده؛ P20 و P21 یکی نشده‌اند؛ P22 Context و P23 Parked باقی مانده‌اند. S09 تکمیل یا باز نشده است.


## S05 — Redness / Inflammation / Rash (structural in progress; not Accepted)

### S05 summary

| ID | Map unit type | Relationship | Acceptance | Operational | Main UNKNOWN |
|---|---|---|---|---|---|
| P24 Persistent redness | Problem/presentation | S05 — Mapped; parent of P25/P26 only as Map | Identified — Accepted=No | Undetermined | Definition/boundary; evidence; customer language; safety |
| P25 Flushing | Symptom/manifestation | P24/S05 — Related/Signal | Identified+Linked — Accepted=No | Undetermined | Signal meaning/threshold; definition; customer language |
| P26 Rosacea | Clinical Condition | P24/S05 — Clinical Anchor | Identified+Linked — Accepted=No | Clinical-anchor only | HBI relevance; evidence; referral boundary |
| P27 Eczema/Dermatitis | Clinical Condition/presentation | S05 — Clinical Anchor; parent of P28/P29 only as Map | Identified — Accepted=No | Clinical-anchor only | Family boundary; definition; evidence; customer language |
| P28 Atopic dermatitis | Clinical Condition | P27/S05 — Clinical Anchor | Identified+Linked — Accepted=No | Clinical-anchor only | Boundary with P27; HBI relevance; evidence |
| P29 Allergic contact dermatitis | Clinical Condition | P27/S05 — Clinical Anchor | Identified+Linked — Accepted=No | Clinical-anchor only | Boundary with P27; HBI relevance; evidence |
| P30 Seborrhoeic dermatitis | Clinical Condition | S05↔S02 — Clinical Anchor; cross-shelf only | Identified+Linked — Accepted=No | Clinical-anchor only | Exact S02 relation/ownership; HBI relevance; evidence |
| P31 Psoriasis | Clinical Condition | S05 — Clinical/Referral-sensitive | Identified — Accepted=No | Clinical-anchor only | Referral threshold; HBI relevance; evidence |
| P32 Hives/Urticaria | Clinical Condition/acute presentation | S05 — Safety/Referral-sensitive | Identified — Accepted=No | Safety-referral only | Safety/referral threshold and protocol; evidence |
| P33 Unspecified rash | Presenting Problem/unresolved manifestation | S05 — Mapped; unresolved | Identified — Accepted=No | Undetermined | Definition/boundary; relation to diagnoses; evidence |

### Record P24 — Persistent redness

| Field | Value |
|---|---|
| Map ID | P24 |
| Working name | Persistent redness |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Problem/presentation — Map-listed |
| Map relationship | S05 — Mapped; parent of P25/P26 only as Map |
| Completion / acceptance | Identified — Accepted = No |
| Operational status | Undetermined |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Definition/boundary; evidence; customer language; safety. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P25 — Flushing

| Field | Value |
|---|---|
| Map ID | P25 |
| Working name | Flushing |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Symptom/manifestation — Map-listed |
| Map relationship | P24/S05 — Related/Signal |
| Completion / acceptance | Identified+Linked — Accepted = No |
| Operational status | Undetermined |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Signal meaning/threshold; definition; customer language. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P26 — Rosacea

| Field | Value |
|---|---|
| Map ID | P26 |
| Working name | Rosacea |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition — Map-listed |
| Map relationship | P24/S05 — Clinical Anchor |
| Completion / acceptance | Identified+Linked — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | HBI relevance; evidence; referral boundary. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P27 — Eczema/Dermatitis

| Field | Value |
|---|---|
| Map ID | P27 |
| Working name | Eczema/Dermatitis |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition/presentation — Map-listed |
| Map relationship | S05 — Clinical Anchor; parent of P28/P29 only as Map |
| Completion / acceptance | Identified — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Family boundary; definition; evidence; customer language. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P28 — Atopic dermatitis

| Field | Value |
|---|---|
| Map ID | P28 |
| Working name | Atopic dermatitis |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition — Map-listed |
| Map relationship | P27/S05 — Clinical Anchor |
| Completion / acceptance | Identified+Linked — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Boundary with P27; HBI relevance; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P29 — Allergic contact dermatitis

| Field | Value |
|---|---|
| Map ID | P29 |
| Working name | Allergic contact dermatitis |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition — Map-listed |
| Map relationship | P27/S05 — Clinical Anchor |
| Completion / acceptance | Identified+Linked — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Boundary with P27; HBI relevance; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P30 — Seborrhoeic dermatitis

| Field | Value |
|---|---|
| Map ID | P30 |
| Working name | Seborrhoeic dermatitis |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition — Map-listed |
| Map relationship | S05↔S02 — Clinical Anchor; cross-shelf only |
| Completion / acceptance | Identified+Linked — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05 and §5 Cross-Shelf Relationships. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Exact S02 relation/ownership; HBI relevance; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P31 — Psoriasis

| Field | Value |
|---|---|
| Map ID | P31 |
| Working name | Psoriasis |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition — Map-listed |
| Map relationship | S05 — Clinical/Referral-sensitive |
| Completion / acceptance | Identified — Accepted = No |
| Operational status | Clinical-anchor only |
| Safety / referral | Referral-sensitive per Map; threshold UNKNOWN. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Referral threshold; HBI relevance; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P32 — Hives/Urticaria

| Field | Value |
|---|---|
| Map ID | P32 |
| Working name | Hives/Urticaria |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Clinical Condition/acute presentation — Map-listed |
| Map relationship | S05 — Safety/Referral-sensitive |
| Completion / acceptance | Identified — Accepted = No |
| Operational status | Safety-referral only |
| Safety / referral | Safety/Referral-sensitive per Map; protocol/threshold UNKNOWN. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Safety/referral threshold and protocol; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### Record P33 — Unspecified rash

| Field | Value |
|---|---|
| Map ID | P33 |
| Working name | Unspecified rash |
| Operational definition | UNKNOWN; structural placement only, no added clinical definition. |
| In scope | As listed in live Map §4 / S05. |
| Out of scope | Diagnosis, treatment, Need, Product, and unsupported medical claims. |
| Unit type | Presenting Problem/unresolved manifestation — Map-listed |
| Map relationship | S05 — Mapped; unresolved |
| Completion / acceptance | Identified — Accepted = No |
| Operational status | Undetermined |
| Safety / referral | UNKNOWN unless explicitly classified above in Map. |
| Evidence / provenance | `SKIN_PROBLEM_SPACE_MAP_V0.1.md` §4 S05. |
| Customer language | UNKNOWN |
| UNKNOWN / GAP | Definition/boundary; relation to diagnoses; evidence. |
| Review note | Structural registration only; Map placement ≠ medical validation ≠ Accepted. |


### S05 relationships (no silent merging)

| ID | Map relationship | Working disposition |
|---|---|---|
| P24 | S05 — Mapped | Problem/presentation; structural parent of P25/P26 only as mapped |
| P25 | P24/S05 — Related/Signal | Identified+Linked; separate manifestation |
| P26 | P24/S05 — Clinical Anchor | Identified+Linked; Clinical-anchor only |
| P27 | S05 — Clinical Anchor | Structural parent of P28/P29 only as mapped; separate records |
| P28 | P27/S05 — Clinical Anchor | Identified+Linked; Clinical-anchor only |
| P29 | P27/S05 — Clinical Anchor | Identified+Linked; Clinical-anchor only |
| P30 | S05↔S02 — Clinical Anchor | Cross-shelf reference only; S02 unchanged |
| P31 | S05 — Clinical/Referral-sensitive | Clinical-anchor only; referral threshold UNKNOWN |
| P32 | S05 — Safety/Referral-sensitive | Safety-referral only; protocol UNKNOWN |
| P33 | S05 — Mapped | Unresolved presentation; no diagnosis inferred |
| P06 | S01→S05 — Clinical Anchor | Reference only; existing S01 record not rewritten |

No relation beyond the live Map is inferred. P24/P25/P26 remain separate; P27/P28/P29 remain separate; P30 does not reopen S02; P31/P32 are not Ordinary-care; P33 remains unresolved. S02 is not expanded or rewritten.


## روابط خوشه (بدون ادغام خاموش)

| ID | نقش نسبت به P01 | وضعیت |
|----|------------------|--------|
| P01 | Primary | Scoped؛ Deferred — **PO-confirmed** |
| P02 | Related / Merge-candidate | Identified + Linked — **PO-confirmed** |
| P07 | Child / Related | Identified + Linked — **PO-confirmed** |
| P05 | Related مستقل هم‌قفسه | Identified/Scoped — **PO-confirmed مرز** |
| P06 | Clinical Condition / inflammatory presentation؛ S01→S05 Clinical Anchor | Identified؛ Accepted نیست؛ عملیاتی Clinical-anchor only؛ مستقل از P01 |

---

## وضعیت مسیر کار

| مرحله | وضعیت |
|--------|--------|
| قالب حداقلی | تثبیت |
| P01+P02+P07+P05 | **PO-confirmed** (هیچ‌کدام Accepted نهایی نیستند) |
| P06 | **ثبت ساختاری**؛ Identified؛ Clinical-anchor only |
| پایلوت ساختاری S01 | **CLOSED** (ساختاری/ارجاعی — نه پزشکی)
| قفسهٔ S02 | **ثبت ساختاری شده**؛ P03/P04؛ نه Accepted |
| G1 / G8 | خارج از دامنهٔ این Closure |
| قفسهٔ S03 | **ثبت ساختاری شده**؛ P08–P16؛ نه Accepted |
| قفسهٔ S04 | **ثبت ساختاری شده**؛ P17–P23؛ نه Accepted |
| قفسهٔ S04 | **در حال کار ساختاری**؛ P17–P23؛ نه Accepted |
| S05–S10 | باز نشده‌اند؛ نیازمند دستور صریح PO |
| Need / Product | خارج از دامنه |

---

## قاعدهٔ نگهداری

- فقط: `docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md`
- کامنت Issue جایگزین این سند نیست.
- Accepted یا وضعیت عملیاتی قطعی فقط با تصمیم صریح PO.
- انتقال پوشه یا تکثیر مرجع متعارف ممنوع.
