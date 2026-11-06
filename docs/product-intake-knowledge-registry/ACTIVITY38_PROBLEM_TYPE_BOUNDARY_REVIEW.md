# فعالیت ۳۸ — فهرست پایه بازبینی مرز انواع واحدهای بانک مشکلات پوستی

**شناسه:** HBI-ACTIVITY-38-BOUNDARY-INVENTORY  
**تاریخ ممیزی اولیه:** 2026-11-06  
**مخزن:** `vahidmaghsoudi2/hbi`  
**منبع اصلی:** `docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md` در `master`  
**Map blob SHA:** `c57ce7edbcee513dcb60b735ce91b98de22d8aa2`  
**وضعیت:** WORKING INVENTORY / NOT ACCEPTED / HUMAN REVIEW REQUIRED

## ۱. هدف و محدودیت

این سند خروجی اولیه فعالیت ۳۸ است: ثبت یک فهرست واحد از P01–P61 و کنار هم قرار دادن نوع ثبت‌شده در Map، دسته‌بندی اولیه قابل استخراج از همان عبارت، Disposition و ارجاع‌های متقاطع. این سند **طبقه‌بندی نهایی پزشکی یا عملیاتی نیست** و هیچ Problem، Need، Evidence، ProductProblemLink یا وضعیت Recommendation را تأیید نمی‌کند.

طبقه‌بندی اولیه صرفاً بازنویسی محافظه‌کارانه برچسب‌های موجود Map است. هرجا نوع ترکیبی، مبهم یا مرز باز باشد، ابهام حفظ می‌شود؛ داده با حدس به یکی از پنج دسته تحمیل نمی‌شود.

## ۲. قواعد مرزبندی که باید حفظ شوند

- Problem با Symptom/Manifestation یکی نیست؛ بااین‌حال یک Manifestation می‌تواند واحد قابل ثبت در فضای Problem باشد، بدون اینکه خودبه‌خود Need پذیرفته شود.
- Clinical Condition به‌تنهایی Need یا مجوز توصیه محصول نیست.
- Context می‌تواند به کشف و تفسیر کمک کند، اما به‌تنهایی تشخیص یا Need نیست.
- Safety/Referral Signal باید مسیر توقف/ارجاع را فعال کند و با Ordinary Care Need مخلوط نشود.
- Descriptor، Sequela، Clinical subtype، Clinical family و رکوردهای hybrid باید صریحاً تعیین تکلیف شوند؛ نباید بی‌صدا در یکی از دسته‌های بالا ادغام شوند.
- P22 یک Problem مستقل دوم نیست: جایگاه canonical آن S04 است و ردیف S09 فقط cross-reference است.
- P51 در Map قفل شده است: Discovery Context / NOT NEED-LEVEL.
- هیچ‌یک از وضعیت‌های NOT ASSESSED، UNKNOWN، GAP، Deferred یا Clinical-anchor-only معادل consultation_ready نیست.

## ۳. فهرست پایه P01–P61

| ID | نام در Map | نوع ثبت‌شده در Map | دسته اولیه از روی برچسب Map | Disposition در Map | ارجاع متقاطع |
|---|---|---|---|---|---|
| P01 | Dry skin/Xerosis | Problem/Clinical presentation | Problem / presentation | Mapped | — |
| P02 | Dehydration/impaired moisture retention | Manifestation/related presentation | Symptom / Manifestation | MERGE/RELATED TO P01 | — |
| P03 | Oily skin/Seborrhoea | Problem/presentation | Problem / presentation | Mapped | — |
| P04 | Combination skin | State Descriptor | Descriptor / مرز باز | Descriptor, not independent Problem | — |
| P05 | Sensitive skin | Problem/presentation | Problem / presentation | Mapped | — |
| P06 | Irritant dermatitis | Clinical Condition/inflammatory presentation | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P07 | Fissuring/cracking | Manifestation | Symptom / Manifestation | Manifestation, not separate Need | — |
| P08 | Acne | Problem/Clinical presentation | Problem / presentation | Mapped | — |
| P09 | Blackheads/open comedones | Manifestation/subtype | Symptom / Manifestation | Child/Related | — |
| P10 | Whiteheads/closed comedones | Manifestation/subtype | Symptom / Manifestation | Child/Related | — |
| P11 | Inflammatory acne lesions | Manifestation/subtype | Symptom / Manifestation | Child/Related | — |
| P12 | Nodular/cystic acne | Severity/clinical subtype | Clinical Condition / clinical anchor | Clinical/Severity Anchor | — |
| P13 | Acne aftermath/discoloration | Sequela/post-inflammatory presentation | Symptom / Manifestation | Related/Cross-Shelf | — |
| P14 | Folliculitis | Clinical Condition/follicular presentation | Clinical Condition / clinical anchor | Clinical Anchor/HBI relevance unresolved | — |
| P15 | Pseudofolliculitis/razor bumps | Problem/follicular presentation | Problem / presentation | Mapped | — |
| P16 | Sebaceous hyperplasia | Clinical Condition/lesion presentation | Clinical Condition / clinical anchor | Clinical Anchor/HBI relevance unresolved | — |
| P17 | Hyperpigmentation/dark spots | Problem/presentation | Problem / presentation | Mapped | — |
| P18 | Melasma | Clinical Condition | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P19 | Post-inflammatory hyperpigmentation | Sequela/pigmentation presentation | Symptom / Manifestation | Related | — |
| P20 | Hypopigmentation | Problem/presentation | Problem / presentation | Mapped; evidence boundary retained | — |
| P21 | Vitiligo | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Referral-sensitive | — |
| P22 | Sun-related pigmentation | Context/pigmentation presentation | Context | Related/Context | S09↔S04 (Related) |
| P23 | Poikiloderma | Clinical Condition/UV-associated presentation | Clinical Condition / clinical anchor | Parked/Evidence Boundary | — |
| P24 | Persistent redness | Problem/presentation | Problem / presentation | Mapped | — |
| P25 | Flushing | Symptom/manifestation | Symptom / Manifestation | Related/Signal | — |
| P26 | Rosacea | Clinical Condition | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P27 | Eczema/Dermatitis | Clinical Condition/presentation | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P28 | Atopic dermatitis | Clinical Condition | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P29 | Allergic contact dermatitis | Clinical Condition | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P30 | Seborrhoeic dermatitis | Clinical Condition | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P31 | Psoriasis | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Referral-sensitive | — |
| P32 | Hives/Urticaria | Clinical Condition/acute presentation | Clinical Condition / clinical anchor | Safety/Referral-sensitive | — |
| P33 | Unspecified rash | Presenting Problem/unresolved manifestation | Problem / presenting problem؛ manifestation unresolved | Mapped | — |
| P34 | Dermatophytosis/fungal infection | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P35 | Tinea/ringworm | Clinical subtype/manifestation | Symptom / Manifestation؛ clinical subtype | Child/Related | — |
| P36 | Bacterial skin infection | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P37 | Viral skin infection | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P38 | Cutaneous herpes simplex | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P39 | Warts | Clinical Condition/lesion presentation | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P40 | Impetigo | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P41 | Scabies | Clinical Condition/infestation | Clinical Condition / clinical anchor | Clinical/Safety-sensitive | — |
| P42 | Shingles | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Referral-sensitive | — |
| P43 | Uneven skin texture | Problem/presentation | Problem / presentation | Mapped; boundary open | — |
| P44 | Hyperkeratosis | Clinical/structural presentation | Clinical Condition / clinical anchor | Clinical Anchor/boundary open | — |
| P45 | Keratosis pilaris | Clinical Condition/presentation | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P46 | Seborrhoeic keratosis | Clinical Condition/lesion | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P47 | Skin tags | Lesion/benign growth presentation | Lesion / clinical anchor؛ مرز نیازمند بازبینی | Clinical Anchor | — |
| P48 | Moles/nevi | Lesion/clinical anchor | Clinical Condition / clinical anchor | Safety-aware Clinical Anchor | — |
| P49 | Changing mole | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P50 | New/growing skin lesion | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P51 | Chronic UV damage | Context/Discovery Problem | Context | DISCOVERY CONTEXT; NOT NEED-LEVEL | — |
| P52 | Actinic keratosis | Clinical/Safety-sensitive lesion | Clinical Condition / clinical anchor | Safety/Referral | — |
| P53 | Suspicious skin-cancer lesion | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P54 | Suspicious melanoma lesion | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P55 | Bleeding/non-healing lesion | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P56 | Rapid change in lesion size/shape/color | Safety/Referral Signal | Safety / Referral | Safety/Referral | — |
| P57 | Autoimmune/autoinflammatory skin disease | Clinical Domain/Condition Family | Clinical family / مرز باز | Clinical Anchor/broad | — |
| P58 | Cutaneous lupus | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Referral-sensitive | — |
| P59 | Adult-onset dermatomyositis with skin findings | Clinical Condition | Clinical Condition / clinical anchor | Clinical/Referral-sensitive | — |
| P60 | Acanthosis nigricans/systemic-associated skin changes | Clinical/systemic-associated presentation | Clinical Condition / clinical anchor | Clinical Anchor | — |
| P61 | Photosensitivity | Symptom/clinical presentation | مبهم: Symptom ↔ Clinical | Clinical/Context relationship | — |

## ۴. نقاطی که به تصمیم مرزی انسانی نیاز دارند

1. **Descriptor در برابر Problem:** P04 (Combination skin) با برچسب State Descriptor ثبت شده و نباید بدون تصمیم صریح به Problem مستقل تبدیل شود.
2. **Manifestationهای وابسته:** P02، P07، P09–P11، P13، P19 و P25 باید از نظر رابطه با والد/واحد مرجع حفظ شوند؛ Related یا Child بودن به معنی ادغام یا Need مستقل نیست.
3. **Sequela و subtype:** P12، P13، P19 و P35 نیازمند تمایز میان شدت/زیرنوع، پیامد و تظاهر هستند؛ برچسب ترکیبی به‌تنهایی تصمیم نهایی نیست.
4. **Clinical subtype / anchor:** P06، P14، P16، P18، P21، P23، P26–P32، P34–P42، P44–P48 و P52/P57–P60 نیازمند مرزبندی روشن میان ثبت encounter، لنگر بالینی و ارجاع‌اند؛ عنوان بالینی به‌تنهایی مجوز مشاوره محصول نیست.
5. **Context:** P22 و P51 باید Context باقی بمانند مگر تصمیم مستند و انسانی دیگری ثبت شود؛ به‌ویژه قفل NOT NEED-LEVEL برای P51 نباید نقض شود.
6. **Safety / Referral:** P49، P50 و P53–P56 صریحاً Safety/Referral Signal هستند؛ P32، P34، P36–P38، P40–P42 و P52 نیز Safety-sensitive یا Referral-sensitive توصیف شده‌اند. آستانه توقف/ارجاع باید جدا از پیشنهاد Ordinary-care تعیین شود.
7. **Problem با مرز باز:** P20، P33 و P43 در عین Problem/presentation بودن دارای محدودیت شواهد یا unresolved boundary هستند.
8. **مرز باز یا ترکیبی:** P23، P33، P43، P44، P47، P48، P52، P57 و P61 باید جداگانه بازبینی شوند.
9. **P61:** عبارت Symptom/clinical presentation ترکیبی است و نباید بدون تصمیم انسانی به Symptom صرف یا Clinical Condition قطعی تبدیل شود.

## ۵. یافته‌های ممیزی اولیه

- تعداد ردیف‌های Map استخراج‌شده: 62
- تعداد شناسه‌های یکتا: 61
- شناسه‌های مورد انتظار: 61
- شناسه‌های مفقود: هیچ‌کدام
- شناسه‌های دارای بیش از یک ردیف Map: P22؛ P22 به‌صورت canonical + cross-reference ثبت شده است.
- این بررسی فقط Map را مبنا قرار داده است؛ تطبیق نهایی هر ردیف با Working Records و تصمیم‌های ثبت‌شدهٔ PO/متخصص، مرحله بعدی همین فعالیت است.

## ۶. محدودیت‌های پذیرش و Recommendation

این فهرست به هیچ وجه فهرست مجاز Recommendation نیست. تا زمان عبور از فعالیت ۳۷ و تصمیم انسانی مستند:
- هیچ موردی از این سند Accepted یا consultation_ready نمی‌شود.
- Need extraction یا ProductProblemLink از روی این جدول انجام نمی‌شود.
- Safety/Referral فقط به‌عنوان مرز توقف/ارجاع بررسی می‌شود، نه مسیر پیشنهاد محصول.
- موارد Context، Descriptor، Clinical-anchor-only، NOT ASSESSED، UNKNOWN، GAP، Deferred و Parked وارد پیشنهاد محصول نمی‌شوند.

## ۷. معیار خروجی فعالیت ۳۸

برای تکمیل فعالیت ۳۸ باید برای هر P01–P61 این موارد در نسخه بازبینی‌شده ثبت شوند:
1. نوع واحد نهایی و تعریف مرز آن؛
2. نوع رابطه با رکورد والد/فرزند یا cross-reference؛
3. تمایز از Need و محدودیت‌های استنتاج؛
4. طبقه عملیاتی مجاز: ordinary consultation candidate، clinical-anchor only، safety/referral only، context-only، descriptor-only یا deferred؛
5. موارد ابهام و Evidence لازم؛
6. نام/نقش بازبین انسانی و تاریخ تصمیم؛
7. عدم ایجاد Accepted/consultation_ready بدون شواهد و تأیید صریح.

## ۸. وضعیت و گام بعدی

**وضعیت فعالیت ۳۸: IN PROGRESS — SOURCE INVENTORY CREATED; HUMAN BOUNDARY REVIEW PENDING.**

گام بعدی: تطبیق این فهرست با Working Records، ماتریس #472 و قواعد Intake در #492؛ سپس تهیه فهرست موارد نیازمند تصمیم PO/متخصص. این کار نباید به تغییر بالینی یا فعال‌سازی Recommendation منجر شود.

**ارتباط با فعالیت ۳۷:** گزارش ممیزی مستقل 2026-11-06 نتیجه NOT READY داده است. فعالیت ۳۷ همچنان ناقص و مانع پذیرش عملیاتی باقی می‌ماند؛ آغاز فهرست‌برداری فعالیت ۳۸ فقط یک کار خواندنی/ساختاری است و گیت پذیرش فعالیت ۳۷ را دور نمی‌زند.

## ۹. تصمیم Product Owner — 2026-11-06

Product Owner فهرست مرزبندی ساختاری این سند را به‌عنوان **طبقه‌بندی کاری اولیه** تأیید کرد؛ این تأیید دقیقاً با محدودیت‌های زیر معتبر است:

- P04 به‌عنوان Descriptor حفظ می‌شود و Problem مستقل تلقی نمی‌شود.
- P12 به‌عنوان Severity / Clinical subtype حفظ می‌شود.
- P13 و P19 به‌عنوان Sequela حفظ می‌شوند؛ بدون ادغام خاموش.
- P22 فقط یک رکورد canonical در S04 دارد و S09 صرفاً cross-reference است.
- P33 به‌عنوان unresolved presenting problem باقی می‌ماند؛ از آن تشخیص استنتاج نمی‌شود.
- P35 به‌عنوان Clinical subtype / Manifestation حفظ می‌شود؛ با P34 ادغام خودکار نمی‌شود.
- P43 و P44 تا زمان وجود شواهد کافی مرز باز دارند.
- P47 و P48 در مرز Lesion / Clinical anchor باقی می‌مانند و با هم یکی نمی‌شوند.
- P51 قفل Context / Discovery و NOT NEED-LEVEL را حفظ می‌کند.
- P52 به‌عنوان Clinical / Safety-sensitive lesion حفظ می‌شود.
- P57 به‌عنوان Clinical Domain / Condition Family حفظ می‌شود.
- P61 به‌عنوان Symptom / Clinical presentation با رابطه S09↔S10 حفظ می‌شود.
- Safety / Referral از Ordinary Care جدا می‌ماند.

**دامنه تأیید:** ساختار و مرزبندی کاری اولیه؛ نه تشخیص پزشکی، نه اعتبارسنجی بالینی نهایی، نه پذیرش Need، نه consultation_ready، نه ProductProblemLink و نه Recommendation eligibility.

**وضعیت پس از تصمیم PO:** بخش ساختاری اولیه تأیید شده است؛ اما معیار خروج فعالیت ۳۸ هنوز کامل نیست. تطبیق هر ۶۱ رکورد با Working Records، ثبت رابطه/Disposition عملیاتی، مستندکردن Evidence لازم برای موارد باز و بازبینی تخصصی مرزهای بالینی همچنان باقی است.

