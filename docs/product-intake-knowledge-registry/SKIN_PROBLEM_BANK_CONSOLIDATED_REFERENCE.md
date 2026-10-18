# HBI — مرجع یکپارچهٔ بانک مشکلات پوستی

**شناسه:** HBI-SKIN-PROBLEM-BANK-CONSOLIDATED-REFERENCE  
**وضعیت این سند:** مرجع تجمیعیِ کنترل و ادامهٔ کار؛ ثبت واقعیت‌ها و تصمیم‌های تاریخی، نه بازنویسی پزشکی بانک  
**دامنه:** Skin Problem Space Map، سابقهٔ ۹۲→۶۲، مجموعهٔ خام P01–P61، اجرای Problem Bank V1، تصمیم‌های پذیرش، اختلاف‌های باز و مسیر ادامه  
**منبع حقیقت:** وضعیت زندهٔ GitHub و تصمیم‌های ثبت‌شدهٔ PO  
**محدودیت:** این سند مجوز تغییر کد، Schema/API/DB، استخراج Need، رابطهٔ Problem→Product یا Recommendation نیست.

> **قاعدهٔ کار:** این سند تنها نقطهٔ ورود و مرجع تجمیعی برای وضعیت/تاریخچهٔ بانک مشکلات پوستی است. پیش از ایجاد هر سند موازی، ابتدا همین سند به‌روزرسانی شود. اسناد، PRها و کامنت‌های تاریخیِ لینک‌شده در اینجا به‌عنوان مدرک منبع حفظ می‌شوند؛ این سند به‌تنهایی محتوای علمی یا جزئیات ۶۱/۶۲ مورد را جایگزین نمی‌کند و مدرک اصلی را حذف نمی‌کند.

---

## 1. خلاصهٔ مدیریتی

1. **تصمیم تاریخی ۹۲→۶۲ تأیید شده است.** در [Issue #293، کامنت 6242411614](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-6242411614) ثبت شده که ۹۲ مورد اولیه به دستور PO پالایش و به ۶۲ مورد کاهش یافته‌اند. این سابقه نباید دوباره به‌عنوان موضوعی برای کشف مطرح شود.
2. **فهرست دقیق و کامل ۶۲ مورد هنوز در این تطبیق به‌عنوان یک artifact مستقل و قابل‌تأیید بازیابی نشده است.** این وضعیت فقط «در محدودهٔ بررسی‌شده پیدا نشد» است، نه اثبات نبودن آن.
3. **یک فهرست خام ۶۱‌موردی واقعاً در GitHub ثبت شده است.** [Issue #293، کامنت 5968601721](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5968601721) آن را به‌عنوان «61-ITEM DISCOVERY SET (RAW LIST)» ارائه می‌کند و صریحاً منع بازسازی یا ایجاد فهرست موازی را دارد.
4. **نقشهٔ P01–P61 یک artifact ساختاری جداگانه است.** [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md) و [کامنت نقشه 5972920377](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972920377) آن را نقشهٔ فضای مسئله می‌دانند، نه خودبه‌خود بانک نهایی، فهرست Need یا تأیید پزشکی.
5. **سوابق اجرای Problem Bank V1، S01–S10، ممیزی cross-shelf و گیت آمادگی در Issue #293 ثبت شده‌اند.** این سوابق نشان می‌دهند کار قبلی بسیار فراتر از یک نقشهٔ اولیه رفته است؛ بنابراین شروع دوباره از صفر یا اجرای یک دور کشف گسترده بدون شاهد تازه مجاز نیست.
6. **گیت آمادگی پیش از پایلوت نتیجهٔ READY داشته است، اما بانک از نظر استفادهٔ واقعی مشتری اعتبارسنجی میدانی نشده است.** Customer Reality و Customer Language تا زمان استفادهٔ واقعی/پایلوت DEFERRED / NOT VERIFIED باقی می‌مانند.
7. **مهم‌ترین شکاف فعلی، شکاف ردیابی/تطبیق است:** باید مشخص شود فهرست ۶۲‌تایی دقیقاً کجا نگهداری می‌شود و چگونه با فهرست خام ۶۱‌تایی و مجموعهٔ P01–P61 مرتبط است. این رابطه نباید با حدس حل شود.

## 2. واژگان وضعیت و قواعد شواهد

- **VERIFIED:** ادعای محدود و مشخص مستقیماً توسط مدرک نام‌برده پشتیبانی می‌شود.
- **FOUND:** منبع یا artifact پیدا شده؛ این برچسب به‌تنهایی به معنی پذیرش محتوا نیست.
- **PARTIAL:** فقط بخشی از artifact یا شواهد قابل‌تأیید است.
- **NOT FOUND IN REVIEWED SCOPE:** در مسیرها/سوابقی که مشخصاً بررسی شده‌اند پیدا نشد؛ ادعای نبود مطلق نیست.
- **OPEN / UNKNOWN:** شواهد موجود برای نتیجهٔ قطعی کافی نیست.
- **ACCEPTED WITH CONDITIONS / READY:** فقط در محدودهٔ تصمیم ثبت‌شده معتبر است؛ به معنی اعتبارسنجی میدانی، کامل بودن پزشکی، پذیرش همهٔ موارد به‌عنوان Problem/Need یا مجوز پیاده‌سازی نیست.

قواعد غیرقابل‌مذاکره:

- `Problem ≠ Need ≠ Symptom/Manifestation ≠ Diagnosis`.
- `Clinical Condition ≠ automatically canonical HBI Problem`.
- `Medical existence ≠ HBI relevance`.
- `KEEP ≠ canonical admission`; تصمیم‌های KEEP/MERGE/RECLASSIFY/PARK/REMOVE باید با شواهد و معیار مربوط تفسیر شوند.
- سیگنال ایمنی/ارجاع با Need مراقبت معمول یکسان نیست.
- Customer Language فقط با شواهد واقعی مشتری تأیید می‌شود؛ زبان مشتری ساختگی یا استنباط‌شده مجاز نیست.
- منبع علمی باید به ادعای دقیق وصل باشد و روشن کند چه چیزی را اثبات می‌کند و چه چیزی را اثبات نمی‌کند.
- UNKNOWN، GAP، CONFLICT و OPEN باید آشکار بمانند؛ خلأ با فرض پر نشود.
- هیچ امتیاز عددی دلخواه، درصد اطمینان ساختگی یا رابطهٔ Problem→Product بر پایهٔ شباهت واژه/ترکیب به‌تنهایی مجاز نیست.

## 3. تطبیق سه مجموعهٔ عددی — اختلاف را حفظ کنید

| مجموعه | مدرک | چه چیزی را ثابت می‌کند؟ | چه چیزی را ثابت نمی‌کند؟ | وضعیت |
|---|---|---|---|---|
| ۹۲ مورد اولیه | [Issue #293، کامنت 6242411614](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-6242411614) | وجود مجموعهٔ تاریخی ۹۲ موردی پیش از پالایش | هویت تک‌تک موارد در نسخهٔ نهایی | VERIFIED به‌عنوان سابقه |
| ۶۲ مورد پس از پالایش | همان کامنت | تصمیم PO برای کاهش مجموعه به ۶۲ مورد | متن کامل، شناسه و disposition هر یک از ۶۲ مورد | تصمیم VERIFIED؛ artifact کامل در محدودهٔ بررسی‌شده NOT FOUND |
| فهرست خام ۶۱‌موردی | [Issue #293، کامنت 5968601721](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5968601721) | artifact خام ۶۱‌موردی با شناسه‌های SK-P01… و منع ساخت فهرست موازی | برابری آن با مجموعهٔ ۶۲‌تایی | FOUND |
| نقشهٔ P01–P61 / ده shelf | [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md)، [کامنت 5972920377](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972920377) | ساختاردهی فضای کشف به ده گروه و ثبت مرزها/هم‌پوشانی‌ها/شکاف‌ها | برابری با ۶۲ مورد یا پذیرش خودکار همهٔ موارد به‌عنوان Problem/Need | FOUND؛ نقشهٔ ساختاری پذیرفته/فریز شده |
| Problem Bank V1 و خروجی‌های S01–S10 | Issue #293 و PRهای #303–#313 | اجرای تحلیل و بازبینی مرحله‌ای روی P01–P61، قواعد روش‌شناختی و ممیزی ساختاری | اعتبارسنجی با مشتری واقعی یا تکمیل قطعی همهٔ مسائل پوستی | سوابق تاریخی FOUND؛ پذیرش با حدود مشخص |

**نتیجهٔ ممنوع:** از تفاوت ۶۲ و ۶۱ نتیجه نگیرید که یک مورد حتماً حذف شده، اضافه شده یا معادل خاصی دارد. تا زمان یافتن تطبیق مستند، رابطهٔ دقیق آن‌ها **OPEN** است.

## 4. نقشه و طبقه‌بندی ساختاری

مرجع نقشه: [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md)  
SHA فعلی فایل در master هنگام این بررسی: `e2c8b881cdfce14dcdbc2da0b94e75eb2f2e7161`.

ده shelf سازمانی/مشاهده‌ای ثبت‌شده:

| Shelf | حوزه | مرز کلی |
|---|---|---|
| S01 | Barrier / Hydration / Surface | خشکی، آب‌رسانی، سطح پوست، حساسیت و سد پوستی |
| S02 | Oil / Sebum / Follicular Balance | چربی، سبوم و ویژگی‌های فولیکولی مرتبط |
| S03 | Acne / Follicular / Pore Presentation | تظاهرات آکنه، فولیکول و منافذ |
| S04 | Pigmentation / Color | تغییرات رنگدانه و رنگ پوست |
| S05 | Redness / Inflammation / Rash | قرمزی، برافروختگی، راش و تظاهرات التهابی |
| S06 | Infection / Infestation | تظاهرات مرتبط با عفونت و آلودگی انگلی |
| S07 | Texture / Keratinization / Surface Growth | بافت، کراتینیزاسیون و برخی رشدهای سطحی |
| S08 | Lesions / Growths / Change | ضایعات، رشدها و تغییراتی که به مرزبندی ایمنی نیاز دارند |
| S09 | Sun / UV-Related Change | زمینه و تغییرات مرتبط با UV/آفتاب |
| S10 | Systemic / Autoimmune / Clinically Significant Skin Presentation | تظاهرات مرتبط با وضعیت‌های سیستمیک یا بالینی مهم |

این shelfها سازمان‌دهی فضای مسئله‌اند، نه taxonomy تشخیصی، بانک درمان یا مجوز توصیه. جزئیات Problem Unit، Boundary/Overlap Register، unknowns و محدودیت‌های شواهد در خود نقشه حفظ می‌شوند؛ آن‌ها را با کپی‌های متنی جدید تکثیر نکنید.

## 5. روش و تصمیم‌های ثبت‌شده برای Problem Bank V1

### 5.1 دستور ماتریس پوشش و پذیرش
[Issue #293، کامنت 5968742916](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5968742916) دستور داد ماتریس Coverage & Acceptance بر مبنای dispositionهای موجود P01–P61 ساخته شود و چهار مرز را بررسی کند:
- ارتباط با محدوده و relevance در HBI؛
- granularity مناسب؛
- مرز شواهد؛
- معنای classification/disposition.

همان دستور منع بازگشایی سلیقه‌ای P01–P61، کشف گستردهٔ تازه، دادهٔ ساختگی مشتری و Need→Product را مشخص کرده است.

### 5.2 دستور اجرای Problem Bank V1
[Issue #293، کامنت 5972984770](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972984770) اجرای Problem Bank V1 را مجاز کرد، با Map V0.1 به‌عنوان baseline پذیرفته/فریز‌شده و بدون مجوز implementation. برای هر shelf باید dispositionها، شکاف‌های پوشش، مرزها و هم‌پوشانی‌ها با شواهد بررسی می‌شدند.

### 5.3 Method Rules & Decision Register
[Issue #293، کامنت 5973634673](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5973634673) این قواعد را ثبت کرد:
- KEEP به‌تنهایی پذیرش canonical نیست.
- Clinical Anchor به‌تنهایی canonical Problem نیست.
- شواهد باید claim-level باشند: Source → Exact Supported Claim → Claim Type → What it proves → What it does NOT prove.
- حل یک مورد تکراری لزوماً شکاف معنایی بزرگ‌تر را نمی‌بندد.
- روش اعتبارسنجی‌شدهٔ S01 نباید برای هر shelf از نو طراحی شود؛ در عین حال، الگوهای کشف‌شده در S01 نباید بدون آزمون به تمام shelfها تعمیم داده شوند.

### 5.4 ممیزی Cross-Shelf و اصلاح P16
- [PR #312](https://github.com/vahidmaghsoudi2/hbi/pull/312) یک snapshot ممیزی است که خطای P16 در آن شناسایی شد؛ به‌عنوان نسخهٔ نهایی استفاده یا بی‌بررسی merge نشود.
- [دستور اصلاح 5979025129 در Issue #293](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979025129) اختلاف را مشخص کرد: P16 باید در S03 باشد، نه S02 یا S07.
- [PR #313](https://github.com/vahidmaghsoudi2/hbi/pull/313) رکورد اصلاح‌شده است؛ سوابق می‌گویند P16 به S03 و بدون رابطهٔ cross-shelf اصلاح شد.
- [نتیجهٔ گیت مستقل 5979176159](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979176159) این موارد را باز نگه داشت: قدرت وضعیت canonical برای P08، معیار پذیرش HBI Relevance، و بازرسی مستقیم artifactهای S01/S02.
- [پذیرش مدیریتی 5979222785](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5979222785) ممیزی اصلاح‌شده را **ACCEPTED WITH CONDITIONS** اعلام کرد؛ این پذیرش، مجوز merge یا implementation نبود.

### 5.5 نتیجهٔ آمادگی پیش از پایلوت
- دستور ممیزی: [کامنت 5982704286](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5982704286).
- نتیجه: [کامنت 5982706812](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5982706812) با نتیجهٔ **READY**.
- این READY به معنی آمادگی ساختاری/روش‌شناختی برای مرحلهٔ کنترل‌شدهٔ بعدی بود؛ نه اثبات کامل بودن بانک، پذیرش هر مورد به‌عنوان Need، اعتبارسنجی مشتری یا مجوز پیاده‌سازی.

## 6. موجودی اسناد و سوابق قبلی

| مدرک | محل | وضعیت/نحوهٔ استفاده |
|---|---|---|
| سابقهٔ ۹۲→۶۲ | [Issue #293 comment 6242411614](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-6242411614) | سابقهٔ رسمی تصمیم PO؛ برای تعداد و رابطهٔ تاریخی است، نه جزئیات هر مورد |
| فهرست خام ۶۱‌موردی | [Issue #293 comment 5968601721](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5968601721) | artifact منبع برای مجموعهٔ SK-P01…؛ بازسازی یا ساخت فهرست موازی ممنوع |
| نقشهٔ ساختاری | [SKIN_PROBLEM_SPACE_MAP_V0.1.md](SKIN_PROBLEM_SPACE_MAP_V0.1.md) و [کامنت 5972920377](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5972920377) | Map V0.1؛ مرجع shelfها، روابط، مرزها، unknowns و شکاف‌های ساختاری |
| روش و قواعد تصمیم | [Issue #293 comment 5973634673](https://github.com/vahidmaghsoudi2/hbi/issues/293#issuecomment-5973634673) | روش قابل استفادهٔ مجدد؛ از طراحی دوباره جلوگیری می‌کند |
| S03 | [PR #303](https://github.com/vahidmaghsoudi2/hbi/pull/303) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود؛ وضعیت فعلی master را از وضعیت PR استنتاج نکنید |
| S04 | [PR #304](https://github.com/vahidmaghsoudi2/hbi/pull/304) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| S05 | [PR #305](https://github.com/vahidmaghsoudi2/hbi/pull/305) و [PR #306](https://github.com/vahidmaghsoudi2/hbi/pull/306) | #306 نسخهٔ scope-corrected معرفی شده؛ وضعیت‌های PR را پیش از هر استفادهٔ اجرایی دوباره بررسی کنید |
| S06 | [PR #307](https://github.com/vahidmaghsoudi2/hbi/pull/307) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| S07 | [PR #308](https://github.com/vahidmaghsoudi2/hbi/pull/308) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| S08 | [PR #309](https://github.com/vahidmaghsoudi2/hbi/pull/309) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| S09 | [PR #310](https://github.com/vahidmaghsoudi2/hbi/pull/310) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| S10 | [PR #311](https://github.com/vahidmaghsoudi2/hbi/pull/311) | artifact مرحله‌ای/تاریخی؛ PR هنگام بررسی باز بود |
| Cross-shelf snapshot اولیه | [PR #312](https://github.com/vahidmaghsoudi2/hbi/pull/312) | نسخهٔ superseded؛ خطای P16 دارد؛ مرجع نهایی نیست |
| Cross-shelf audit اصلاح‌شده | [PR #313](https://github.com/vahidmaghsoudi2/hbi/pull/313) | اصلاح P16 و سوابق گیت/پذیرش مرتبط؛ هنگام بررسی PR باز بود، بنابراین آن را با محتوای master یکی نگیرید |
| رجیستری دانش محصول/مشکلات | [PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md](PRODUCT_INTAKE_EVIDENCE_KNOWLEDGE_REGISTRY.md) | رجیستری گسترده‌تر سه حوزه؛ این سند، مرجع متمرکز برای تطبیق تاریخچهٔ بانک مشکلات است |
| نقشه‌راه سه حوزه | [ROADMAP_THREE_DOMAINS.md](ROADMAP_THREE_DOMAINS.md) | اصول بالادستی و رابطهٔ سه حوزه؛ جایگزین جزئیات/تصمیم‌های بانک نیست |
| پیشنهادهای PO | [PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md](PRODUCT_OWNER_PROPOSALS_MAGHSOUDI.md) | بیان هدف و ترجیحات PO؛ قرارداد اجرایی یا مجوز پیاده‌سازی نیست |

**نکتهٔ repository reality:** چندین artifact در سوابق PR/Issue موجودند ولی در بررسی فعلی به‌عنوان فایل ادغام‌شده در master تأیید نشدند. باز بودن یک PR به معنی پذیرش یا baseline بودن فایل آن نیست؛ پذیرش یک اجرای تاریخی نیز به معنی ادغام فایل یا تأیید وضعیت فعلی master نیست. هر گزارش وضعیت باید این سه حالت را جدا کند.

## 7. موارد باز واقعی و محدودیت‌های پذیرفته‌شده

| مورد | وضعیت | اقدام مجاز/لازم |
|---|---|---|
| artifact کامل ۶۲ مورد | NOT FOUND IN REVIEWED SCOPE | جست‌وجوی هدفمند در سوابق/PRها/فایل‌های موجود و ثبت محل دقیق؛ نه بازسازی حدسی |
| رابطهٔ ۶۲ با فهرست خام ۶۱ و P01–P61 | OPEN | فقط با تطبیق موردبه‌مورد مستند حل شود؛ هیچ هم‌ارزی فرض نشود |
| معیار دقیق HBI Relevance برای پذیرش canonical | OPEN | طبق تصمیم‌های بعدی PO/قرارداد معتبر حل شود؛ با اصلاح سلیقه‌ای پیش‌نویس‌ها حل نشود |
| قدرت وضعیت canonical برای P08 | OPEN | حفظ شود تا معیار رسمی روشن شود؛ گزارش READY آن را خودبه‌خود حل نکرده است |
| بررسی مستقیم artifactهای S01/S02 در audit تاریخی | PARTIAL در رکورد گیت | به‌عنوان محدودیت تاریخی ذکر شود؛ ادعای بازرسی کامل نکنید |
| Customer Reality / Customer Language | DEFERRED UNTIL PILOT / NOT VERIFIED | پس از استفادهٔ واقعی HBI با شواهد واقعی ارزیابی شود؛ زبان مشتری ساخته نشود |
| کامل بودن بانک در دنیای واقعی | UNPROVEN | نتیجهٔ READY را به ادعای جامعیت یا اعتبارسنجی میدانی تبدیل نکنید |
| اجرای واقعی HBI / runtime | خارج از این مرجع | از این سند برای نتیجه‌گیری runtime استفاده نکنید |

## 8. گام اجرایی بعدی — محدود و مشخص

**هدف:** بستن تطبیق منبع ۶۲‌موردی با سوابق موجود، نه شروع تحقیق پزشکی یا بازنویسی بانک.

1. منابع همین سند را مبنای جست‌وجو قرار دهید؛ ابتدا کامنت کامل ۶۱ موردی، PRها/شاخه‌های S01–S10 و هر artifact مرتبطی که در سوابق به آن‌ها ارجاع شده است بررسی شوند.
2. فقط در صورت یافتن سند/محتوای مستقیم، مسیر، SHA/شناسهٔ کامنت و وضعیت دقیق ۶۲ مورد ثبت شود.
3. اگر پس از بررسی هدفمند همچنان فهرست ۶۲ موردی بازیابی نشد، وضعیت را **NOT FOUND IN REVIEWED SCOPE** نگه دارید و دقیقاً محدودهٔ بررسی را ذکر کنید. این نتیجه مجوز بازسازی ۶۲ مورد از روی P01–P61 نیست.
4. اگر تطبیق موردبه‌مورد سندیت ندارد، رابطهٔ ۶۲↔۶۱↔P01–P61 همچنان OPEN می‌ماند؛ از شمارش یا شباهت اسامی نتیجه‌گیری نکنید.
5. در این مرحله فهرست تازه، ماتریس تازه، taxonomy تازه یا فیلدهای جدید ایجاد نکنید. این سند را پس از کشف مدرک موجود اصلاح کنید.
6. بعد از بسته‌شدن تطبیق، فقط شکاف‌های اثبات‌شده برای تصمیم PO فهرست شوند؛ کار قبلاً پذیرفته‌شده از نو اجرا نشود.

## 9. مرز نهایی

این مرجع، سابقه و وضعیت را یک‌جا قابل‌پیگیری می‌کند. وجود این سند به‌تنهایی:
- Problem Bank V1 را دوباره باز نمی‌کند؛
- P01–P61 را به فهرست ۶۲ مورد تبدیل نمی‌کند؛
- Customer Reality/Language را VERIFIED نمی‌کند؛
- Need extraction/acceptance یا Problem→Product را مجاز نمی‌کند؛
- مجوز تغییر Recommendation، scoring، schema، API، DB، UI یا پیاده‌سازی نیست.

**اصل پایان:** KEEP → COMPLETE → CHANGE → BUILD. ابتدا شواهد و خروجی‌های قبلی حفظ و تطبیق شوند؛ فقط شکاف واقعی و اثبات‌شده کار تازه ایجاد می‌کند.
