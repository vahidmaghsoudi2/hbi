# HBI — رکوردهای کاری بانک مشکلات پوستی (S01 بسته؛ S02 در حال کار ساختاری)

**شناسه:** HBI-SKIN-PROBLEM-BANK-WORKING-RECORDS  
**ناوبری مرجع:** [فهرست عملیاتی](SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md) ← [مرجع تجمیعی](SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md) ← همین رکوردهای کاری؛ برای مرزهای ساختاری به [نقشهٔ پیش‌نویس (DRAFT / NOT THE ACTIVE PROBLEM BANK)](SKIN_PROBLEM_SPACE_MAP_V0.1.md) مراجعه کنید.  
**وضعیت:** **S01 STRUCTURALLY CLOSED; S02 STRUCTURAL WORK IN PROGRESS** (2026-10-22) — S01 فقط از نظر مرز/ارجاع بسته است؛ S02 فقط ثبت کاری ساختاری است؛ **هیچ مورد جدیدی Accepted پزشکی/بانک نهایی نیست**  
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

## S02 — Oil / Sebum / Follicular Balance (در حال کار ساختاری؛ نه Accepted)

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
| قفسهٔ S02 | **در حال کار ساختاری**؛ P03/P04؛ نه Accepted |
| G1 / G8 | خارج از دامنهٔ این Closure |
| S02 | **در حال کار ساختاری**؛ P03 و P04 ثبت شده‌اند؛ منتظر بازبینی PO |
| S03–S10 | باز نشده‌اند؛ نیازمند دستور صریح PO |
| Need / Product | خارج از دامنه |

---

## قاعدهٔ نگهداری

- فقط: `docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md`
- کامنت Issue جایگزین این سند نیست.
- Accepted یا وضعیت عملیاتی قطعی فقط با تصمیم صریح PO.
- انتقال پوشه یا تکثیر مرجع متعارف ممنوع.
