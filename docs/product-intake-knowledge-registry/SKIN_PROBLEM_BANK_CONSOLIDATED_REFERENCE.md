# HBI — مرجع واحد برای بانک مشکلات پوستی

> **نقطهٔ ورود عملیاتی تیم:** [SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md](SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md) — فهرست مرجع‌ها، قواعد ثبت تغییرات و شکاف‌های باقی‌مانده. این فهرست جایگزین محتوای این مرجع یا منابع تخصصی نمی‌شود.

> **رکوردهای کاری فعلی:** [SKIN_PROBLEM_BANK_WORKING_RECORDS.md](SKIN_PROBLEM_BANK_WORKING_RECORDS.md) — رکوردهای کاری P01–P07؛ این رکوردها به فهرست مرجع مشکلات پوستی پیوند دارند، اما به‌خودی‌خود اعتبارسنجی پزشکی یا مجوز پیشنهاد محصول ایجاد نمی‌کنند. P06 فقط Clinical Anchor است.

**شناسه:** HBI-SKIN-PROBLEM-BANK-CONSOLIDATED-REFERENCE  
**وضعیت:** مرجع تجمیعی کاری؛ باید با تصمیم‌های PO و وضعیت زندهٔ GitHub به‌روز بماند.  
**دامنه:** ثبت نقشهٔ مشکلات پوستی P01–P61 به‌عنوان فهرست مرجع تعیین‌شده توسط مالک پروژه، همراه با مرزبندی‌ها، شواهد و تصمیم‌های قبلی، وضعیت اسناد پشتیبان و شکاف‌های باقی‌مانده.  
**مرجع فعال بالادستی:** [نقشه‌راه سه حوزه](ROADMAP_THREE_DOMAINS.md)، [Issue #403](https://github.com/vahidmaghsoudi2/hbi/issues/403)، [پیشنهادهای مالک پروژه](PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md) و [ثبت کنترل‌شدهٔ منابع](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md).  
**محدودیت:** این سند به‌تنهایی مجوز تغییر کد، Schema/API/DB، استخراج Need، رابطهٔ Problem→Product یا Recommendation نیست.

> **قاعدهٔ ادامه:** تصمیم‌های تأییدشده دوباره باز نمی‌شوند. نقشهٔ مشکلات پوستی P01–P61 مبنای فهرست مرجع جاری است. این تصمیم، آن را به اعتبارسنجی پزشکی، Need Bank یا مجوز پیشنهاد محصول تبدیل نمی‌کند. مواد منسوخ به‌عنوان ورودی فعال یا در خلاصه‌های تحویل تکثیر نمی‌شوند. پیش از ساخت هر سند موازی، همین مرجع به‌روزرسانی می‌شود. مدارک اصلی برای ردیابی حفظ می‌شوند، اما وضعیت و اختیار آن‌ها باید مطابق منابع فعال زیر تفسیر شود.

---

## 1. تصمیم‌ها و مرجعیت فعلی

1. **فهرست مرجع مشکلات پوستی، نقشهٔ P01–P61 است.** طبق تصمیم جاری مالک پروژه، همین نقشه به‌عنوان فهرست مشکلات پوستی استفاده می‌شود و نیازی به بازسازی فهرست موازی نیست. سوابق تاریخی PR #407 برای ردیابی تصمیم‌های پیشین حفظ می‌شوند، اما شماره‌گذاری‌های قدیمی مبنای مرجع جاری نیستند.
2. **این سند مرجع تجمیعی وضعیت و تاریخچه است.** نقشهٔ P01–P61 لینک‌شده در همین پوشه، فهرست مرجع مشکلات پوستی است. حدود و برچسب‌های هر مورد مطابق متن نقشه حفظ می‌شوند؛ این تصمیم ادعای اعتبارسنجی پزشکی ایجاد نمی‌کند.
3. **نقشهٔ P01–P61 فهرست مرجع مشکلات پوستی است، نه فهرست Need یا مجوز پیشنهاد محصول.** [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md) مرزها، shelfها و موارد نامعلوم را ثبت می‌کند؛ پذیرش آن به‌عنوان فهرست مرجع، معادل تأیید پزشکی یا مجوز درمان نیست.
4. **تصمیم جاری مالک پروژه بر برچسب‌های تاریخی اولویت دارد.** نقشه از این پس فهرست مرجع مشکلات پوستی است؛ وضعیت پیش‌نویس آن فقط به معنی نبود اعتبارسنجی پزشکی/Need/Product است، نه اینکه استفاده از آن به‌عنوان فهرست مرجع ممنوع باشد.
5. **Issue #293 اکنون ردیاب فعال بانک مشکلات نیست.** طبق [Issue #396](https://github.com/vahidmaghsoudi2/hbi/issues/396) و [ثبت کنترل‌شدهٔ منابع](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md)، کامنت‌های مشخص آن برای سابقه و ممیزی قابل استفاده‌اند؛ بدنهٔ فعلی Issue #293 نباید به‌عنوان داشبورد جاری بانک مشکلات استفاده شود.
6. **مسیر محصول، بانک مشکلات و لایهٔ ارتباط به هم وابسته‌اند، اما یک کار واحد نیستند.** [Issue #403](https://github.com/vahidmaghsoudi2/hbi/issues/403) و [نقشه‌راه سه حوزه](ROADMAP_THREE_DOMAINS.md) مسیر کلی را مشخص می‌کنند؛ قرارداد ورود محصول و ردیاب‌های عملیاتی موجود جای خود را حفظ می‌کنند.

## 2. قواعد مفهومی و شواهد

- Problem ≠ Need ≠ Symptom/Manifestation ≠ Diagnosis.
- Clinical Condition ≠ automatically canonical HBI Problem.
- وجود علمی یا پزشکی یک وضعیت به‌تنهایی ارتباط عملیاتی آن با HBI را اثبات نمی‌کند.
- KEEP ≠ canonical admission؛ هر disposition باید در محدوده و با معیار مستند خود خوانده شود.
- سیگنال ایمنی/ارجاع با نیاز مراقبت معمول یکی نیست.
- زبان مشتری فقط با شواهد واقعی مشتری تأیید می‌شود؛ عبارت مشتری، مشاهدهٔ اپراتور، نظر پزشک، اصطلاح علمی و استنباط AI باید جدا بمانند.
- ادعای سازنده ≠ واقعیت علمی مستقل‌شده ≠ اثربخشی محصول نهایی.
- شواهد مربوط به یک ماده به‌تنهایی اثربخشی یا ایمنی محصول نهایی را اثبات نمی‌کند.
- هر ادعای مهم باید به منبع قابل‌بازیابی و ادعای دقیق وصل باشد: منبع، نوع گزاره، آنچه پشتیبانی می‌کند، آنچه پشتیبانی نمی‌کند، محدودیت و تاریخ در صورت اهمیت.
- UNKNOWN، GAP، CONFLICT، OPEN و PENDING باید آشکار بمانند؛ خلأ با حدس پر نشود.
- امتیازدهی عددی، درصد اطمینان ساختگی و رتبه‌بندی بهترین/بدترین محصول مجاز نیست.
- شباهت واژگانی، وجود یک ترکیب یا ادعای تبلیغاتی به‌تنهایی مجوز رابطهٔ Problem→Product نیست.
- خروجی AI پیش‌نویس قابل بررسی است؛ تأیید محتوا و تصمیم نهایی باید طبق گیت‌های معتبر انجام شود.

## 3. منابع فعال و نقش هرکدام

| منبع | نقش معتبر فعلی | محدودیت |
|---|---|---|
| [PR #407](https://github.com/vahidmaghsoudi2/hbi/pull/407) | ثبت تاریخی دستور PO دربارهٔ فهرست مرجع و عدم تکرار پالایش | سابقهٔ تصمیم پیشین است؛ وضعیت جاری مطابق تصمیم فعلی PO و نقشهٔ P01–P61 خوانده شود |
| [ROADMAP_THREE_DOMAINS.md](ROADMAP_THREE_DOMAINS.md) | نقشه‌راه مشترک دانش محصول، بانک مشکلات و ارتباط مبتنی بر شواهد | جایگزین قرارداد تخصصی یا مجوز implementation نیست |
| [Issue #403](https://github.com/vahidmaghsoudi2/hbi/issues/403) | مرجع بالادستی ترتیب مراحل، دروازه‌ها و سه حوزهٔ وابسته | تغییر کد/داده یا merge را به‌خودی‌خود مجاز نمی‌کند |
| [PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md](PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md) | هدف و تصمیم‌های اجرایی پیشنهادی PO؛ شامل بازیابی خروجی پذیرفته‌شده و انتخاب موضوع ساده برای پایلوت | هر پیشنهاد باید با قراردادهای مصوب و وضعیت زندهٔ مخزن تطبیق داده شود |
| [PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md) | مرجع فعال تعیین وضعیت منابع قدیمی، متعارض و جایگزین‌شده | به معنی حذف تاریخچه یا تأیید محتوای همهٔ منابع نیست |
| [PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md](PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md) | فهرست مرجع‌های محصول، دانش، شواهد و وضعیت اسناد | SHAها و وضعیت‌های تاریخ‌دار باید پیش از گزارش وضعیت جاری دوباره بررسی شوند |
| [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md) | نقشهٔ ساختاری پشتیبان برای Problem Space و شناسه‌های P01–P61 | طبق register جاری، DRAFT / UNACCEPTED؛ بانک نهایی، Need Bank یا تأیید پزشکی نیست |
| [Issue #293](https://github.com/vahidmaghsoudi2/hbi/issues/293) | منبع تاریخی برای تصمیم‌ها و کامنت‌های معین بانک مشکلات | ردیاب فعال بانک مشکلات نیست؛ فقط کامنت‌های مشخص و مرتبط را استفاده کنید |
| [Issue #396](https://github.com/vahidmaghsoudi2/hbi/issues/396) | سابقهٔ ممیزی منابع و روش نگهداری دانش | چک‌لیست بازیابی منبع منسوخ‌شده نباید دوباره به‌عنوان مأموریت فعال اجرا شود |

## 4. ساختار Problem Space

نقشهٔ پشتیبان ده shelf سازمانی را تعریف می‌کند. این گروه‌بندی‌ها ساختار مشاهده و مرزبندی‌اند، نه taxonomy تشخیصی و نه طبقه‌بندی درمان:

| Shelf | حوزه | مرز اصلی |
|---|---|---|
| S01 | Barrier / Hydration / Surface | خشکی، آب‌رسانی، سطح پوست و سد پوستی |
| S02 | Oil / Sebum / Follicular Balance | چربی، سبوم و ویژگی‌های فولیکولی |
| S03 | Acne / Follicular / Pore Presentation | تظاهرات آکنه، فولیکول و منافذ |
| S04 | Pigmentation / Color | تغییرات رنگدانه و رنگ |
| S05 | Redness / Inflammation / Rash | قرمزی، برافروختگی، راش و تظاهرات التهابی |
| S06 | Infection / Infestation | تظاهرات مرتبط با عفونت یا آلودگی انگلی |
| S07 | Texture / Keratinization / Surface Growth | بافت، کراتینیزاسیون و برخی رشدهای سطحی |
| S08 | Lesions / Growths / Change | ضایعات و تغییرات نیازمند مرزبندی ایمنی |
| S09 | Sun / UV-Related Change | زمینه و تغییرات مرتبط با UV/آفتاب |
| S10 | Systemic / Autoimmune / Clinically Significant Presentation | تظاهرات مرتبط با وضعیت‌های سیستمیک یا بالینی مهم |

**قواعد استفاده از نقشه:**
- شناسه‌های P01–P61 را برای ردیابی منابع موجود حفظ کنید؛ برای پرکردن شکاف‌ها فهرست موازی نسازید.
- قرارگرفتن یک مورد در shelf به معنی پذیرش آن به‌عنوان Need یا مناسب‌بودن برای مراقبت عادی نیست.
- تفکیک Problem/Presentation، Symptom/Manifestation، Clinical Condition، Context، Potential Need و Safety/Referral حفظ شود.
- روابط بین shelfها باید از رابطهٔ تکراریِ «Problem مستقل» جدا بمانند.
- هیچ رابطهٔ محصولی از خود نقشه استنتاج نمی‌شود.

## 5. سابقهٔ تصمیم‌های پیشین و وضعیت جاری — 2026-10-18

این بخش، نتیجهٔ جست‌وجوی تکمیلی را ثبت می‌کند تا در دور بعد همان مسیرها دوباره از ابتدا بررسی نشوند.

### شواهد مستقیم پیدا‌شده

- [PR #407](https://github.com/vahidmaghsoudi2/hbi/pull/407) ادغام شده و دستور تاریخی مالک پروژه را ثبت می‌کند؛ تصمیم جاری این است که نقشهٔ P01–P61 فهرست مرجع مشکلات پوستی باشد. توضیح PR می‌گوید تغییر آن، به‌روزرسانی register و افزودن پیشنهادهای مالک پروژه بوده است.
- [Commit b6a9514](https://github.com/vahidmaghsoudi2/hbi/commit/b6a9514957429160dafcc7e47abe2842d82d4690) همین تصمیم را در پیام کامیت تأیید می‌کند؛ این commit خودِ فهرست را در پیام یا فایل جداگانه ارائه نمی‌کند.
- [PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md](PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md)، بخش «مرحله یک — تثبیت خروجی پالایش‌شدهٔ پذیرفته‌شده»، می‌گوید نسخهٔ پذیرفته‌شده باید بازیابی و به مرجع فعال قابل ارجاع تبدیل شود؛ همچنین تصریح می‌کند که مالک پروژه نباید برای بازگویی یا اجرای مجدد کار قبلی درخواست شود.
- [Issue #293 comment 5968601721](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5968601721) متن Discovery Map را در خود دارد؛ [comment 5972984770](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972984770) مأموریت Problem Bank V1 را بر همان نقشه ثبت می‌کند. این سوابق برای ردیابی تاریخی حفظ می‌شوند.
- [Issue #396](https://github.com/vahidmaghsoudi2/hbi/issues/396) و کامنت‌های بازیابی آن، مسیرهای تاریخی جست‌وجوشده و تصمیم کنترل‌شدهٔ نگهداری منابع را مستند می‌کنند. این سوابق به‌عنوان تاریخچه حفظ می‌شوند؛ چک‌لیست منسوخ‌شدهٔ آن Issue دوباره به مأموریت فعال تبدیل نمی‌شود.

### نتیجهٔ جست‌وجوی تکمیلی

| محل بررسی‌شده | نتیجه |
|---|---|
| بدنه و کامنت‌های مرتبط Issue #293 | تصمیم‌ها و فهرست خام Discovery Set پیدا شد؛ متن کامل خروجی پالایش‌شدهٔ موردنظر در کامنت‌های بررسی‌شده شناسایی نشد |
| PR #407، diff و commit ادغام‌شده | تصمیم و تغییر register تأیید شد؛ فهرست مرجع در تغییرات PR وجود ندارد |
| سند پیشنهادهای مالک پروژه و register فعال در master | دستور بازیابی و ادامه از خروجی پذیرفته‌شده پیدا شد؛ خود فهرست در این اسناد درج نشده است |
| درخت فایل‌های master و نام‌های اسناد مرتبط | فایل مستقلی که آشکارا همان خروجی پذیرفته‌شده را نگه دارد، شناسایی نشد |
| جست‌وجوی GitHub code و جست‌وجوی کتابخانهٔ فایل‌های مکالمه | تطبیق قطعی با متن کامل خروجی پذیرفته‌شده پیدا نشد؛ جست‌وجوی code گزارش `incomplete_results` داشته، پس نتیجه را نباید پوشش کامل همهٔ تاریخچه دانست |

**وضعیت جاری:** `OWNER-DESIGNATED SKIN PROBLEM LIST = P01–P61 MAP`.

این بخش فقط تاریخچهٔ جست‌وجوهای پیشین را نگه می‌دارد. طبق تصمیم جاری مالک پروژه، نقشهٔ P01–P61 فهرست مرجع مشکلات پوستی است و از این پس نباید به‌عنوان فهرستی جدا از مرجع جاری معرفی شود.

### تکمیل جست‌وجو — 2026-10-19

در دور تکمیلی، کامنت‌های Issue #293 به‌صورت کامل دوباره بازیابی شدند و با سوابق Issue #396 و نتایج جست‌وجوی کتابخانه تطبیق داده شدند.

- [Issue #293 comment 6242411614](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-6242411614) صرفاً رابطهٔ تاریخی پالایش را ثبت می‌کند؛ متن کامل و موردبه‌موردِ خروجی پذیرفته‌شده در خود این کامنت وجود ندارد.
- [Issue #396 comment 6216799980](https://github.com/vahidmaghsoudi2/hbi/issues/396#issuecomment-6216799980) می‌گوید بازیابی فهرست، پیش‌شرط کار بازنشست‌سازی منابع نیست و جست‌وجوی بیشتر بدون بازگشایی از سوی PO نباید ادامه یابد. دستور فعلی PO برای ادامهٔ کار، در این نوبت به‌عنوان بازگشایی محدودِ مسیر بازیابی تفسیر شد؛ این اجازه به معنی اجازهٔ بازسازی یا تکرار پالایش نیست.
- [Issue #396 comment 6217203410](https://github.com/vahidmaghsoudi2/hbi/issues/396#issuecomment-6217203410) تأیید می‌کند که PR #397 ادغام شده و رجیستر بازنشست‌سازی مرجع فعال منابع قدیمی است.
- جست‌وجوی دوبارهٔ کامنت‌های مرتبط Issue #293، بحث‌های PRهای shelf و فایل‌های کتابخانه، خروجی مستقل و کاملِ پذیرفته‌شده را آشکار نکرد. فایل‌های پیدا‌شده شامل ممیزی مجموعهٔ خام Discovery هستند و با خروجی پذیرفته‌شده یکی فرض نمی‌شوند.

**نتیجهٔ تصمیم جاری:** نقشهٔ P01–P61 به‌عنوان فهرست مرجع مشکلات پوستی ثبت شد. یادداشت‌های بازیابی بالا صرفاً سابقه‌اند و دیگر مانع استفاده از این فهرست نیستند.

### گام بعدی بدون تکرار پالایش

1. اگر منبع اصلی در یک چت یا فایل قبلی بازیابی شود، همان متن عیناً به این مرجع لینک/ثبت شود؛ هیچ پالایش مجددی انجام نشود.
2. اگر در مسیرهای باقی‌ماندهٔ تاریخچه نیز مدرک اصلی پیدا نشد، فقط همین شکاف و محل‌های بررسی‌شده ثبت بماند؛ کاربر برای بازگویی یا اجرای مجدد فرایند قبلی فراخوانده نشود.
3. پس از بازیابی، کار به اولویت‌بندی خروجی پذیرفته‌شده و انتخاب یک موضوع ساده برای پایلوت ادامه یابد.

## 5. وضعیت تعارض‌ها و موارد باز

ثبت کنترل‌شدهٔ منابع، موارد زیر را باز یا حل‌نشده نگه می‌دارد. سابقهٔ اصلاح یک draft به‌تنهایی برای بستن تعارض در وضعیت جاری کافی نیست:

| موضوع | وضعیت فعلی برای ادامه | قاعده |
|---|---|---|
| جایگاه و پذیرش نهایی نقشه | DRAFT / UNACCEPTED طبق register فعال | به عبارت‌های تاریخی «فریز» یا «آماده» به‌عنوان وضعیت جاری تکیه نکنید |
| P16 | تعارض نگاشت/طبقه‌بندی در سوابق | تا تعیین مرجع جاری و تصمیم قابل ردیابی، حل‌شده اعلام نشود |
| P22 | هم‌پوشانی S04/S09 | رابطهٔ زمینه‌ای/رنگدانه را با Problem مستقل اشتباه نگیرید |
| P46/P47 | ارتباط S07/S08 | وضعیت و مرز هر مورد باید مستند شود |
| P51/P52/P61 | ارتباطات S09/S08/S10 و مرز context/condition/safety | هیچ موردی را صرفاً از روی جایگاه shelf به Need تبدیل نکنید |
| P08 و معیار HBI Relevance | وضعیت پذیرش و معیار relevance نیازمند مرجع جاری روشن | «وجود پزشکی» را معادل «پذیرش در HBI» نگیرید |
| S01/S02 | کامل‌بودن محتوای جزئی و منبع‌های مستقیم در master اثبات نشده | PRهای draft جایگزین محتوای ادغام‌شده نیستند |
| Customer Reality / Customer Language | NOT VERIFIED | عبارت یا الگوی مشتری ساخته نشود؛ پس از دسترسی به شواهد واقعی بررسی شود |
| خروجی پالایش‌شدهٔ پذیرفته‌شده | پذیرش فهرست تأیید شده؛ فایل/نسخهٔ کامل هنوز در بررسی master به‌عنوان مرجع مستقل مشخص نشده | فقط از سوابق موجود بازیابی و محل دقیق آن ثبت شود؛ بازسازی یا تکرار پالایش ممنوع |
| کامل‌بودن پزشکی کل بانک | اثبات نشده | READY ساختاری تاریخی، ادعای جامعیت علمی نیست |

## 6. وضعیت اسناد کاری تاریخی

وضعیت جاری از register فعال بررسی شد؛ PRهای زیر در وضعیت draft/unmerged هستند و فایل‌هایشان را نباید به‌عنوان محتوای پذیرفته‌شدهٔ master معرفی کرد:

- S03: [PR #303](https://github.com/vahidmaghsoudi2/hbi/pull/303)
- S04: [PR #304](https://github.com/vahidmaghsoudi2/hbi/pull/304)
- S05: [PR #306](https://github.com/vahidmaghsoudi2/hbi/pull/306)؛ [PR #305](https://github.com/vahidmaghsoudi2/hbi/pull/305) جایگزین/منسوخ‌شده نسبت به #306 است.
- S06: [PR #307](https://github.com/vahidmaghsoudi2/hbi/pull/307)
- S07: [PR #308](https://github.com/vahidmaghsoudi2/hbi/pull/308)
- S08: [PR #309](https://github.com/vahidmaghsoudi2/hbi/pull/309)
- S09: [PR #310](https://github.com/vahidmaghsoudi2/hbi/pull/310)
- S10: [PR #311](https://github.com/vahidmaghsoudi2/hbi/pull/311)
- Cross-shelf audit: [PR #313](https://github.com/vahidmaghsoudi2/hbi/pull/313)؛ [PR #312](https://github.com/vahidmaghsoudi2/hbi/pull/312) به‌عنوان snapshot superseded ثبت شده است.
- برنامهٔ شواهد زبان مشتری: [PR #314](https://github.com/vahidmaghsoudi2/hbi/pull/314)، draft/unmerged؛ محتوایش را نباید به‌عنوان baseline ادغام‌شده معرفی کرد.

کامنت‌های تاریخی مشخص برای ردیابی روش و گیت‌ها:
- [Map V0.1 — comment 5972920377](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972920377)
- [Method rules — comment 5973634673](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5973634673)
- [Cross-shelf correction — comment 5979025129](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979025129)
- [Management acceptance with conditions — comment 5979222785](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979222785)
- [Customer Reality status — comment 5979521659](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979521659)
- [Pre-pilot readiness result — comment 5982706812](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5982706812)

این سوابق برای توضیح تصمیم تاریخی مفیدند؛ وضعیت جاری باید با register فعال، master فعلی و PR state تطبیق داده شود. پذیرش مشروط یا گیت READY تاریخی، خودبه‌خود فایل را merge نمی‌کند و شکاف‌های ثبت‌شده در منابع فعال را نمی‌بندد.

## 7. روند کار مورد تأیید

1. **ادامه از خروجی پذیرفته‌شده:** نسخهٔ ذخیره‌شده را در سوابق موجود پیدا و مسیر/شناسه/نسخهٔ دقیق آن را ثبت کنید. از مالک پروژه نخواهید کار قبلی را دوباره توضیح دهد.
2. **فقط مدرک مستقیم:** اگر artifact پیدا شد، محتوای اصلی را ارزیابی کنید؛ نام فایل یا اشارهٔ یک گزارش به‌تنهایی اثبات وجود/کامل‌بودن نیست.
3. **بدون بازسازی حدسی:** اگر نسخهٔ ذخیره‌شده پیدا نشد، محل‌های دقیق بررسی‌شده و نتیجه را ثبت کنید؛ محتوای پذیرفته‌شده را از روی نقشه یا draftهای پراکنده دوباره نسازید.
4. **فقط شکاف واقعی:** بعد از بازیابی، اختلاف‌های واقعی میان نسخهٔ پذیرفته‌شده و مدارک جاری مشخص شوند. تصمیم‌های بسته‌شده دوباره باز نشوند.
5. **موضوع ساده برای پایلوت:** طبق پیشنهاد PO، پس از تثبیت دسترسی به خروجی پذیرفته‌شده، یک نگرانی پرتکرار با ابهام و حاشیهٔ بالینی کمتر انتخاب شود؛ سپس بستهٔ بررسی استاندارد با منابع مجاز آماده گردد.
6. **بازبینی انسانی:** شواهد، ابهام‌ها، ملاحظات ایمنی و موارد نیازمند بررسی اپراتور/پزشک روشن بمانند.
7. **محصول و ارتباط:** تیم/فرایند محصول به‌صورت مستقل ویژگی‌ها و ادعاهای محصولات واقعی را منبع‌دار ثبت می‌کند؛ لایهٔ ارتباط فقط پس از تعریف نوع رابطه و معیار شواهد می‌تواند این دو حوزه را متصل کند.
8. **بدون پیاده‌سازی ضمنی:** هیچ‌یک از مراحل بالا به‌تنهایی مجوز schema/API/DB، Recommendation، امتیازدهی یا merge نیست.

## 8. مرز این سند

این سند فقط یک نقطهٔ ورود تجمیعی برای وضعیت و منابع بانک مشکلات است. آن را به داشبورد موازی برای G8، وضعیت runtime، Product Intake یا Recommendation تبدیل نکنید. برای آن حوزه‌ها از مراجع جاری ثبت‌شده در [نقشه‌راه سه حوزه](ROADMAP_THREE_DOMAINS.md)، [رجیستری دانش](PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md) و [ثبت کنترل‌شدهٔ منابع](PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md) استفاده کنید.

**اصل پایانی:** تصمیم پذیرفته‌شده را حفظ کن؛ نسخهٔ اصلی را بازیابی کن؛ وضعیت جاری را از مرجع فعال بخوان؛ فقط شکاف اثبات‌شده را پیگیری کن؛ تاریخچه را با وضعیت جاری اشتباه نگیر.


## 9. PO decision — bounded structural review of P01/P02 (2026-10-20)

**Decision status:** PO-confirmed for this bounded structural pilot; this does not accept a canonical Problem Bank item or provide medical validation.

### P01 — Dry skin / Xerosis
- Working record status: `Scoped`, ready for structural review; the operational definition remains explicitly **proposed**, not a verified statement from Map V0.1.
- Operational disposition: `Deferred` for now. `Ordinary-care candidate` is not approved by this decision.
- Customer language, medical validation, and any safety/referral thresholds remain unknown unless separately supported by direct evidence.

### P02 — Dehydration / impaired moisture retention
- Status: `Identified + Linked` to P01; not independently Scoped and not Accepted.
- Map V0.1 classifies P02 as a manifestation/related presentation and records `MERGE/RELATED TO P01`; B01 says no independent Need distinction is established.
- Decision: retain option C — Merge-candidate pending human/PO review. Do not merge operationally, delete the ID, or claim a separate accepted Problem.
- Independent operational status remains undetermined. No standalone `Ordinary-care candidate` status is authorized for P02.

### Open questions for the structural review
1. Is the proposed P01 boundary acceptable as a working definition?
2. Should P02 remain a separately tracked linked record, or only be displayed under P01? No separate-counting rule is inferred.
3. What evidence, if any, would justify an independent operational definition for P02?

**Source boundary:** These decisions use Map V0.1 and the PO-confirmed review of the P01/P02 working records. Map placement is not medical validation, Need acceptance, treatment authorization, or product mapping. The Map is now the owner-designated Skin Problem List; this designation does not alter other shelf, P05, Need, Product, application, DB, Schema/API, or G8 state.

## ثبت یافته‌های بررسی منابع — 2026-10-22

این بخش در همین مرجع تجمیعی ثبت می‌شود؛ سند موازیِ فهرست منابع ایجاد نمی‌شود.

- **مرجع ساختاری فعال:** همین مرجع تجمیعی، [فهرست عملیاتی](SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md) و [رکوردهای کاری](SKIN_PROBLEM_BANK_WORKING_RECORDS.md) در مسیر `docs/product-intake-knowledge-registry/` هستند. [PR #409](https://github.com/vahidmaghsoudi2/hbi/pull/409) ساختار ناوبری را تثبیت کرده و [Issue #410](https://github.com/vahidmaghsoudi2/hbi/issues/410) ممیزی همان تغییر است.
- **ردیاب حاکمیتی:** [Issue #403](https://github.com/vahidmaghsoudi2/hbi/issues/403) برای نقشهٔ راه و وضعیت فاز است؛ جایگزین این مرجع، فهرست عملیاتی یا رکوردهای کاری نیست.
- **سوابق تصمیم ساختاری S01:** [PR #413](https://github.com/vahidmaghsoudi2/hbi/pull/413)، [PR #414](https://github.com/vahidmaghsoudi2/hbi/pull/414) و [PR #419](https://github.com/vahidmaghsoudi2/hbi/pull/419) برای سابقه و ممیزی‌اند؛ وضعیت ادغام/اعتبار هرکدام باید از GitHub زنده خوانده شود و سابقهٔ PR به‌تنهایی پذیرش پزشکی نیست.
- **بازبینی اسناد:** [PR #430](https://github.com/vahidmaghsoudi2/hbi/pull/430) سابقهٔ ممیزی اسناد است؛ [PR #412](https://github.com/vahidmaghsoudi2/hbi/pull/412)، [PR #416](https://github.com/vahidmaghsoudi2/hbi/pull/416) و [PR #417](https://github.com/vahidmaghsoudi2/hbi/pull/417) صرفاً سوابق مرتبط برای بررسی وضعیت زنده‌اند، نه مرجع جایگزین.
- **تصمیم جاری PO:** نقشهٔ P01–P61 به‌عنوان فهرست مرجع مشکلات پوستی استفاده می‌شود. جست‌وجو برای فهرست‌های موازی متوقف است؛ محتوا از همین مرجع خوانده می‌شود.
- **مرزهای لازم‌الحفظ:** P01 = خشکی پوست/Xerosis، Scoped و Deferred، نه Accepted. P07 = ترک/شکاف پوست، مرتبط با P01 اما با شناسهٔ مستقل؛ ادغام P01/P07 ممنوع. P02 فقط Linked به P01؛ P05 مستقل و Related؛ P06 همچنان Clinical Anchor است.

**اقدام نگهداری:** یافته‌های این بررسی در همین مرجع تجمیعی ثبت می‌شوند. فهرست عملیاتی فقط ناوبری می‌کند و رکوردهای کاری محل جزئیات رکوردها و روابط باقی می‌مانند. هیچ فایل موازی برای تکرار این یافته‌ها مرجعیت پیدا نمی‌کند.
