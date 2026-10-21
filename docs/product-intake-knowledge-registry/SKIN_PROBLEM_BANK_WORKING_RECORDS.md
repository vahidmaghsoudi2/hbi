# HBI — رکوردهای کاری بانک مشکلات پوستی (خوشهٔ خشکی / S01)

**شناسه:** HBI-SKIN-PROBLEM-BANK-WORKING-RECORDS  
**ناوبری مرجع:** [فهرست عملیاتی](SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md) ← [مرجع تجمیعی](SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md) ← همین رکوردهای کاری؛ برای مرزهای ساختاری به [نقشهٔ پیش‌نویس (DRAFT / NOT THE ACTIVE PROBLEM BANK)](SKIN_PROBLEM_SPACE_MAP_V0.1.md) مراجعه کنید.  
**وضعیت:** **S01 PILOT STRUCTURALLY CLOSED** (2026-10-22) — مرزها و ارجاعات بسته؛ **هیچ موردی Accepted پزشکی/بانک نهایی نیست**  
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
| S02–S10 | باز نشده تا دستور صریح PO |
| زبان مشتری / آستانه‌های ایمنی قطعی | عمدتاً UNKNOWN |

### قواعد قفل‌شده پس از Closure

1. تصمیم‌های PO برای P01/P02/P05/P07 بدون مدرک جدید و تأیید صریح PO تغییر نمی‌کنند.
2. P06 به خشکی ساده فروکاسته نمی‌شود.
3. Map placement ≠ medical validation ≠ Accepted.
4. shelf بعدی فقط پس از بازبینی و تأیید این PR توسط PO.

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
| پایلوت ساختاری S01 | **CLOSED** (ساختاری/ارجاعی — نه پزشکی) |
| G1 / G8 | خارج از دامنهٔ این Closure |
| سایر shelfها | باز نشوند تا بازبینی این Closure و دستور PO |
| Need / Product | خارج از دامنه |

---

## قاعدهٔ نگهداری

- فقط: `docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md`
- کامنت Issue جایگزین این سند نیست.
- Accepted یا وضعیت عملیاتی قطعی فقط با تصمیم صریح PO.
- انتقال پوشه یا تکثیر مرجع متعارف ممنوع.
