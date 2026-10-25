# HBI — فهرست عملیاتی واحد کار بانک مشکلات پوستی

**وضعیت:** منتشرشده روی `master` پس از ادغام PR #409 در 2026-10-20. این فهرست نقطهٔ ورود ناوبری است؛ نقشهٔ P01–P61 طبق تصمیم PO فهرست مرجع مشکلات پوستی است.  
**هدف:** یک نقطهٔ ورود برای تیم، شش مرجع/بستهٔ کاری و ثبت روشن شکاف‌ها؛ جلوگیری از ویرایش پراکنده و ایجاد مرجع موازی.  
**قاعدهٔ کار:** تا پایان این واحد کار، تغییرات اسنادی مربوط به بانک مشکلات پوستی باید از مسیر همین پوشهٔ `docs/product-intake-knowledge-registry/` و شاخه/PR کاری تأییدشده انجام شود. هیچ تغییری در برنامه، کد، DB، Schema، API، دادهٔ محصول یا G8 از این سند مجاز نمی‌شود. PR #409 خودِ بستهٔ تغییرات GitHub است و نمی‌تواند به‌عنوان فایل داخل پوشه ذخیره شود.

## 0. وضعیت پایلوت‌ها (به‌روز ۲۰۲۶-۱۰-۲۲)

| مورد | وضعیت |
|------|--------|
| پایلوت ساختاری S01 | **CLOSED** — مرز و ارجاع؛ نه پذیرش پزشکی |
| رکوردهای کاری | [SKIN_PROBLEM_BANK_WORKING_RECORDS.md](SKIN_PROBLEM_BANK_WORKING_RECORDS.md) — P01, P02, P05, P06, P07 |
| ارزیابی آمادگی مشاوره و صف بازبینی انسانی S01 | [بخش S01 در Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md#s01--ارزیابی-آمادگی-مشاوره-و-صف-بازبینی-انسانی-اسنادی-نه-accepted) — ارزیابی اسنادی؛ نه Accepted؛ وضعیت‌های Accepted/Need/Product/G8 تغییر نمی‌کنند. |

| فهرست مرجع مشکلات پوستی | [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md) — مرجع تعیین‌شده توسط PO؛ بدون ادعای اعتبارسنجی پزشکی/Need/Product |
| G1 (تعیین مرجع فهرست مشکلات پوستی) | CLOSED — Map P01–P61 طبق تصمیم PO فهرست مرجع است |
| G8 | BLOCKED / NOT VERIFIED |
| S01 | **CLOSED** ساختاری/ارجاعی — نه پذیرش پزشکی |
| S02 | **در حال کار ساختاری** — P03/P04 نه Accepted؛ [ارزیابی آمادگی مشاوره و صف بازبینی انسانی S02](SKIN_PROBLEM_BANK_WORKING_RECORDS.md#s02--ارزیابی-آمادگی-مشاوره-و-صف-بازبینی-انسانی-اسنادی-نه-accepted) در Working Records |
| S03 | **ثبت ساختاری شده + ارزیابی آمادگی مشاوره (اسنادی؛ نه Accepted)** — [بخش S03 در Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md#s03--ارزیابی-آمادگی-مشاوره-و-صف-بازبینی-انسانی-اسنادی-نه-accepted)؛ P08–P16؛ P13 فقط Cross-Shelf به S04؛ P16 مسیر Map برابر S02→S07؛ هیچ `consultation_ready` ثبت نشده است. |
| S04 | **ثبت ساختاری شده** — P17–P23 در [Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md)؛ نه Accepted؛ P22 Context با ارجاع به S09؛ P23 Parked/Evidence Boundary با مرز S04↔S09؛ S09 باز نشده. |
| S05 | **در حال کار ساختاری** — P24–P33 در [Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md)؛ نه Accepted؛ P06 فقط ارجاع S01→S05؛ P30 رابطهٔ S05↔S02 بدون بازنویسی S02؛ P31/P32 مرزهای Clinical/Referral/Safety را حفظ می‌کنند. |
| S06 | **ثبت ساختاری شده** — P34–P42 در [Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md)؛ نه Accepted؛ قفسهٔ Clinical/Safety؛ P39 فقط ارجاع متقاطع S06↔S08؛ S08 باز نشده. |
| S07 | **ثبت ساختاری شده** — P43–P47 در [Working Records](SKIN_PROBLEM_BANK_WORKING_RECORDS.md)؛ نه Accepted؛ P43/P44 boundary open؛ P46/P47 فقط ارجاع S07↔S08؛ P16 فقط ارجاع S02→S07. |
| S08 | **ثبت ساختاری شده** — P48–P50 و P53–P56؛ خوشهٔ Safety/Referral طبق Map §6 B06؛ نه Accepted و نه Ordinary-care؛ P39/P46/P47 فقط ارجاع متقاطع؛ P51/P52 در S09 می‌مانند. |
| S09 | **ثبت ساختاری شده** — P51 (Context؛ locked disposition؛ NOT ACCEPTED / NOT ELIGIBLE for V1 Need / no automatic safety flag) و P52 (Clinical/Safety-sensitive؛ S09↔S08)؛ P22 فقط ارجاع S09↔S04 به رکورد موجود؛ نه Accepted/Need/Product. |
| S10 | **ثبت ساختاری شده** — P57–P61 طبق Map زنده؛ Clinical/Referral-sensitive، Clinical Anchor و Context؛ نه Accepted/Need/Product. |


## 1. اسناد مرجع این حوزه در GitHub

**نقطهٔ ورود فعلی این واحد کار:** همین فهرست عملیاتی و سپس [مرجع تجمیعی بانک مشکلات پوستی](SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md).


**رکوردهای کاری پایلوت:** [SKIN_PROBLEM_BANK_WORKING_RECORDS.md](SKIN_PROBLEM_BANK_WORKING_RECORDS.md).

این پوشه محل گردآوری ناوبری و اسناد جاری مرتبط است؛ سند تجمیعی، وضعیت منابع، شکاف‌های معلوم و گام بعدی را نشان می‌دهد. نقشهٔ P01–P61 مرجع فهرست مشکلات پوستی است؛ وضعیت‌های ساختاری/بالینی هر مورد مطابق همان سند حفظ می‌شود.

## 2. PR #409 — بستهٔ تثبیت مرجع

[بازکردن PR #409](https://github.com/vahidmaghsoudi2/hbi/pull/409)

**وضعیت ادغام (2026-10-20):** [PR #409](https://github.com/vahidmaghsoudi2/hbi/pull/409) با موفقیت در `master` ادغام شد. ممیزی مستقل [Issue #410](https://github.com/vahidmaghsoudi2/hbi/issues/410) تکمیل و بسته شد (PASS WITH EXPLICIT LIMITS). این انتشار کنترل‌های ناوبری/مرجع را تثبیت کرد؛ G1 طبق تصمیم جاری PO بسته است و G8 همچنان BLOCKED / NOT VERIFIED است.

### 2.1 شماره‌های اجرایی مرتبط — فهرست پیوندی واحد

این فهرست فقط برای یافتن سابقه‌هاست؛ **محتوا، تصمیم یا جدولِ سندهای دیگر اینجا کپی نمی‌شود**. مرجع جاری هر موضوع در بخش‌های بالا و در فایل تخصصی خودش باقی می‌ماند. رکوردهای قدیمی/پیش‌نویس برای تاریخچه‌اند و بر تصمیم جاری PO اولویت ندارند.

| حوزه | شماره‌های GitHub | کاربرد / وضعیت |
|---|---|---|
| ردیاب اصلی | [Issue #403](https://github.com/vahidmaghsoudi2/hbi/issues/403) | ردیاب بالادستی برنامه و مسیر کار Skin Problem Space؛ برای اقدام جاری از همین Index و اسناد مرجع پیروی شود. |
| تثبیت نقطهٔ ورود | [PR #409](https://github.com/vahidmaghsoudi2/hbi/pull/409) · [Issue #410](https://github.com/vahidmaghsoudi2/hbi/issues/410) | ایجاد Workspace Index و ممیزی مستقل تاریخی ناوبری؛ سابقهٔ تثبیت مرجع. |
| رکوردهای آغازین و ممیزی زنده | [PR #413](https://github.com/vahidmaghsoudi2/hbi/pull/413) · [PR #414](https://github.com/vahidmaghsoudi2/hbi/pull/414) · [PR #430](https://github.com/vahidmaghsoudi2/hbi/pull/430) | ثبت‌های اولیهٔ P01/P02/P05/P06/P07 و ممیزی وضعیت؛ برای وضعیت فعلی به Working Records و Map رجوع شود. |
| ثبت ساختاری قفسه‌ها S01–S10 | [#419](https://github.com/vahidmaghsoudi2/hbi/pull/419) · [#420](https://github.com/vahidmaghsoudi2/hbi/pull/420) · [#421](https://github.com/vahidmaghsoudi2/hbi/pull/421) · [#422](https://github.com/vahidmaghsoudi2/hbi/pull/422) · [#423](https://github.com/vahidmaghsoudi2/hbi/pull/423) · [#424](https://github.com/vahidmaghsoudi2/hbi/pull/424) · [#425](https://github.com/vahidmaghsoudi2/hbi/pull/425) · [#426](https://github.com/vahidmaghsoudi2/hbi/pull/426) · [#427](https://github.com/vahidmaghsoudi2/hbi/pull/427) · [#428](https://github.com/vahidmaghsoudi2/hbi/pull/428) | سابقهٔ ثبت ساختاری قفسه‌ها؛ ثبت ساختاری به معنی Accepted/Need/Product یا اعتبارسنجی پزشکی نیست. |
| تعیین مرجع فهرست P01–P61 | [PR #433](https://github.com/vahidmaghsoudi2/hbi/pull/433) · [PR #435](https://github.com/vahidmaghsoudi2/hbi/pull/435) | مبنای جاریِ تعیین Map P01–P61 به‌عنوان فهرست مرجع و جلوگیری از فهرست موازی؛ G1 بسته و G8 همچنان مسدود است. |
| تصمیم مرزی P07 و همگام‌سازی S10 | [PR #442](https://github.com/vahidmaghsoudi2/hbi/pull/442) · [PR #444](https://github.com/vahidmaghsoudi2/hbi/pull/444) | P07 مستقل؛ رابطه با P01 برابر UNKNOWN / NOT VERIFIED؛ وضعیت ساختاری S10 با Index هم‌راستا شده است. |
| آمادگی مشاوره و صف بازبینی انسانی | [PR #448 — S01](https://github.com/vahidmaghsoudi2/hbi/pull/448) · [PR #450 — S02](https://github.com/vahidmaghsoudi2/hbi/pull/450) · [PR #451 — S03](https://github.com/vahidmaghsoudi2/hbi/pull/451) | ثبت اسنادی در Working Records؛ نه Accepted و نه مجوز مشاوره. جزئیات فقط در همان بخش‌های Working Records است. |
| دسترسی از منوی هوم‌پیج | [PR #439 — ساختار مستنداتی](https://github.com/vahidmaghsoudi2/hbi/pull/439) · [PR #441 — منوی عملیاتی](https://github.com/vahidmaghsoudi2/hbi/pull/441) | PR #441 ادغام شده و «دانشنامه ← دانش پوست» به همین Workspace Index پیوند دارد؛ منو فهرست P01–P61 را تکثیر نمی‌کند. |
| مسیر مفهومی سه‌حوزه‌ایِ مرتبط | [PR #404](https://github.com/vahidmaghsoudi2/hbi/pull/404) · [PR #405](https://github.com/vahidmaghsoudi2/hbi/pull/405) · [PR #447](https://github.com/vahidmaghsoudi2/hbi/pull/447) | سابقهٔ نقشه‌راه و مفهوم رابطهٔ مشکل–محصول؛ جایگزین Map یا Working Records نیست. |
| پیش‌نویس‌ها و بررسی‌های تاریخی | [PR #295](https://github.com/vahidmaghsoudi2/hbi/pull/295) · [#303](https://github.com/vahidmaghsoudi2/hbi/pull/303) · [#304](https://github.com/vahidmaghsoudi2/hbi/pull/304) · [#305](https://github.com/vahidmaghsoudi2/hbi/pull/305) · [#306](https://github.com/vahidmaghsoudi2/hbi/pull/306) · [#307](https://github.com/vahidmaghsoudi2/hbi/pull/307) · [#308](https://github.com/vahidmaghsoudi2/hbi/pull/308) · [#309](https://github.com/vahidmaghsoudi2/hbi/pull/309) · [#312](https://github.com/vahidmaghsoudi2/hbi/pull/312) · [#313](https://github.com/vahidmaghsoudi2/hbi/pull/313) · [#314](https://github.com/vahidmaghsoudi2/hbi/pull/314) · [#315](https://github.com/vahidmaghsoudi2/hbi/pull/315) · [#412](https://github.com/vahidmaghsoudi2/hbi/pull/412) · [#416](https://github.com/vahidmaghsoudi2/hbi/pull/416) · [#417](https://github.com/vahidmaghsoudi2/hbi/pull/417) | فقط سابقه؛ این‌ها را به‌جای مرجع جاری استفاده نکنید. به‌ویژه #312 به‌عنوان snapshot جایگزین‌شده و نتیجهٔ قدیمی «61/62» در #417 نباید بر تصمیم جاری PO در #433 غلبه کند. اعتبار/بازنشستگی منبع را در [Source Retirement Register](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md) بررسی کنید. |

**مرز دامنه:** شماره‌های مربوط به پروندهٔ ویژگی‌ها و ورود محصولات پوستی (مانند PR #411، #446 و #449) در این فهرست بانک مشکلات ادغام نمی‌شوند؛ آن‌ها حوزهٔ محصول دارند و باید در مرجع محصولی خود بمانند. این جداسازی برای جلوگیری از مخلوط‌شدن «مشکل پوستی» با «محصول پوستی» است.

---

## 3. نقشهٔ راه سه حوزه

[ROADMAP_THREE_DOMAINS.md](ROADMAP_THREE_DOMAINS.md)

این سند جهت‌گیری و مرزبندی سه حوزه را تعیین می‌کند: دانش محصول، بانک مشکلات پوستی، و رابطهٔ مستدل میان مشکل/نیاز و ویژگی/شواهد محصول. نقشهٔ راه جایگزین قرارداد تخصصی، ثبت شواهد یا بانک پذیرفته‌شده نیست.

## 4. ثبت منابع و تعیین اعتبار

[PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md)

این ثبت، وضعیت منابع را مشخص می‌کند: فعال، پیش‌نویس، تاریخی یا جایگزین‌شده. تاریخچه حذف نمی‌شود، اما منابع تاریخی نباید بدون تصمیم صریح دوباره به مسیر فعال تبدیل شوند.

## 5. ثبت شواهد و دانش محصول

[PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md](PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md)

این سند برای ردیابی شواهد، ادعاها، منابع و وضعیت دانش محصول است؛ جایگزین بانک مشکلات یا تصمیم بالینی نیست.

## 6. ثبت اجرای کار

[PRODUCT_INTAKE_EXECUTION_LOG.md](PRODUCT_INTAKE_EXECUTION_LOG.md)

این سند برای ثبت اقدام‌ها، وضعیت اجرا و شواهد تکمیل است. وضعیت جاری هر مرحله باید همراه با تاریخ و مرجع GitHub تأیید شود.

---

## شکاف‌های باقی‌مانده — فهرست اقدام، نه دور جدید کشف

| شناسه | شکاف | اقدام لازم | وضعیت |
|---|---|---|---|
| G1 | مرجع جاری فهرست مشکلات پوستی تعیین نشده بود. | مالک پروژه Map P01–P61 را فهرست مرجع تعیین کرد؛ فهرست موازی نسازید. | بسته شد با تصمیم PO |
| G2 | انتشار مرجع تجمیعی و هشدارهای منابع قدیمی روی master. | PR #409 ادغام شد. | تکمیل شد |
| G3 | آزمون پذیرش ناوبری. | کنترل‌های اصلی با #409 و ممیزی #410. | تکمیل با محدودیت‌های صریح |
| G4 | مرز «مرجع کاری» با «بانک نهایی». | پیوند Index ↔ Working Records ↔ Map در Closure S01 تقویت شد. | در حال تثبیت با PR Closure |
| G5 | پروتکل ثبت تغییرات آینده. | همین Index + Working Records. | عملیاتی |
| S01-C | بستن ساختاری پایلوت S01 | جدول وضعیت P01–P07/P06 در Working Records | این PR |

## پروتکل ویرایش تا پایان این واحد کار

1. این پوشه نقطهٔ کاری واحد برای اسناد این حوزه است؛ از ساخت مرجع موازی خودداری کنید.
2. پیش از هر تغییر، شاخه، PR و نسخهٔ زندهٔ فایل را بررسی کنید.
3. مرجع تجمیعی = وضعیت و ناوبری؛ Retirement Register = اعتبار منابع؛ Evidence Registry = شواهد محصول؛ Execution Log = اقدام‌ها؛ Roadmap = جهت؛ Working Records = رکوردهای پایلوت ساختاری.
4. نقشهٔ P01–P61 را فهرست مرجع مشکلات پوستی بدانید؛ UNKNOWN / GAP و مرزبندی‌های ثبت‌شده را حفظ کنید.
5. پس از هر تغییر، لینک‌ها و وضعیت GitHub را بررسی کنید.
6. مستندات و ناوبری فقط؛ بالینی/محصولی/کد/G8 خارج از دامنه.

## معیار پایان این واحد کار (ناوبری)

- [x] G2 و بخش عمدهٔ G3 با PR #409 و Issue #410 بسته شدند.
- [x] PR #409 ادغام شد.
- [x] پایلوت ساختاری S01 در Working Records بسته شد (این دور).
- [x] G1 با تصمیم PO برای استفاده از Map P01–P61 به‌عنوان فهرست مرجع بسته شد.
- [ ] انتخاب shelf بعدی فقط با دستور PO پس از بازبینی Closure.

**وضعیت ناوبری:** کنترل‌های مرجع روی master فعال‌اند؛ S01 ساختاری بسته و S02 تا S10 ثبت ساختاری شده‌اند. عبور ساختاری Map از S01 تا S10 کامل شد؛ Map فهرست مرجع مشکلات پوستی است، اما Accepted Need/Product از آن استنتاج نمی‌شود. G1 طبق تصمیم PO بسته است؛ G8 همچنان `BLOCKED / NOT VERIFIED` است.


## S10 — آخرین قفسهٔ Map

- **وضعیت:** ثبت ساختاری شده؛ P57–P61 مطابق شناسه‌ها و برچسب‌های Map زنده در Working Records ثبت شده‌اند؛ هیچ‌کدام Accepted یا Need نیستند.
- **مرز:** Clinical/Referral-sensitive و Clinical Anchor فقط نقش ساختاری‌اند؛ Ordinary-care یا Product استنتاج نشده است. P61 رابطهٔ S09↔S10 را صرفاً طبق Map حفظ می‌کند.
- **محدودیت:** G1 = CLOSED BY PO DECISION؛ G8 = BLOCKED / NOT VERIFIED. Draftهای #304/#412/#416 مرجع SSOT نیستند.

**عبور ساختاری Map از S01 تا S10 کامل شد؛ Accepted/Need/Product شروع نشده است.** این عبارت فقط تکمیل ثبت ساختاری قفسه‌ها را اعلام می‌کند، نه پذیرش پزشکی یا تکمیل بانک نهایی.
