# فعالیت ۴۰ — سند نهایی دانش مشاورهٔ رنگ مو HBI

## 1. هدف و وضعیت اعتبار
این سند تجمیع ساختار دانش و محدودیت‌های تصمیم‌گیری تا فعالیت ۳۹ است. **سند نهاییِ معماری/دانش ثبت‌شده** محسوب می‌شود، نه تأیید تخصصی رنگ مو، نه محصول-فرمول معتبر، نه موتور توصیهٔ آمادهٔ مشتری.

طبقه‌بندی هر محتوا:
- `owner_defined`: تصمیم/قاعده مالک پروژه؛ فقط در محدوده ثبت‌شده معتبر.
- `catalog_identity`: شناسه، نام خام، سری یا شماره؛ به‌تنهایی رفتار شیمیایی یا نتیجه را اثبات نمی‌کند.
- `general_scientific_pending_review`: مبانی عمومی نیازمند evidence/review مناسب.
- `product_specific_pending`: ادعای محصول‌محور بدون شناسایی دقیق و evidence قابل استفاده نیست.
- `specialist_pending`: قاعدهٔ تخصصی تا review واقعی pending.
- `anecdotal_signal`: تجربه شبکه اجتماعی یا گزارش فردی؛ قانون عمومی نیست.

## 2. مبانی رنگ و اصطلاحات
موضوعات ثبت‌شده در اسناد پایه: level/depth، underlying pigment، color wheel و neutralization، tone families، تفاوت depth/hue/reflect/intensity، و عوامل اثرگذار بر نتیجه. این اسناد مبنای اصطلاحات و ساختار آموزش هستند؛ هر ادعای شیمیایی یا نسخهٔ تصمیم فنی باید evidence و specialist review داشته باشد.

**محدودیت عکس:** عکس منفرد نمی‌تواند پایهٔ قابل اتکای تعیین pigment، سابقه شیمیایی، ساختار/porosity، امکان‌پذیری دقیق یا فرمول باشد. توصیف تصویری در صورت استفاده، منبع/کیفیت و uncertainty را حفظ می‌کند.

## 3. کاتالوگ و هویت محصول
- Raw catalog labels/codeها حفظ می‌شوند؛ fuzzy matching یا مشابهت کدها به‌تنهایی قبول نمی‌شود.
- ساختار catalog ثبت‌شده شامل ۱۹ سری و ۸۸ code در ماتریس قبلی است؛ این ثبت identity/structure است، نه تأیید عملکرد/chemistry.
- Editorial grouping برای navigation، provisional است و نباید جای label خام یا evidence رسمی را بگیرد.
- شماره/alias فقط در محدودهٔ صریح rule ثبت‌شده پذیرفته می‌شود.
- استثناهای مالک: 6.7، 8.56، 6.53، 6.54 بدون تعیین ویژه به‌صورت ordinary interpretation پردازش نمی‌شوند.
- Natural Extra در مقایسه با Natural Simple متناظر، قاعده مالک پروژه و قوی‌تر تعریف شده؛ این rule **ادعای لیفت شیمیایی، oxidative behavior یا performance** نیست و خارج از scope ثبت‌شده تعمیم نمی‌یابد.

## 4. ورودی‌های مشاوره
Intake باید goal/target، priorities، current base description، regional condition، prior service history، other chemical service history، regional map، safety screen، context/constraints و—برای product-specific claim—exact product identity/evidence را نگه دارد.

هر field دارای value، source (client-reported / professional-observed / documented / image-only / unknown)، confidence و conflict record است. Unknown با «بدون سابقه» یکسان نیست. Conflict در field مؤثر مانع ارزیابی وابسته می‌شود.

### 4.1 Current base
سطح/توصیف پایه یک input descriptive است؛ برآورد تصویری یا uncertain را قطعی نکن. Current base با target preference جداست.

### 4.2 Target
Target preference آزاد، depth/family/tone direction/intensity/maintenance/priorities/unacceptable outcomes/reference و maintenance expectation را ثبت می‌کند. Preference برابر feasibility نیست؛ target change نسخه جدید و fresh evaluation لازم دارد.

### 4.3 Service history
Color، lightening/bleach، toner، direct/plant dye، perm/relaxer، smoothing/keratin، home application و سایر chemical serviceها به‌صورت event و region/source/certainty/date/product detail ثبت می‌شوند. Statusها: known، none reported، unknown، incomplete، conflict. Unknown هرگز none فرض نمی‌شود.

### 4.4 Regional state
Roots/mid-lengths/ends/patches یا map نواحی با داده‌های observation/report/image uncertainty ثبت می‌شوند. تفاوت نواحی نباید در یک average/label محو شود. Porosity/structure و chemistry history از تصویر استنتاج نمی‌شوند.

## 5. Evidence & knowledge controls
Data completeness و knowledge completeness مستقل‌اند.
- `DATA_GAP`: input مورد نیاز missing/unknown؛ سؤال مشخص بپرس.
- `KNOWLEDGE_GAP`: evidence/قاعده معتبر موجود نیست؛ حدس نزن.
- `ENGINE_FAIL`: failure داخلی؛ output همان run را suppress کن.
- Owner decision، catalog snapshot، scientific source، official product evidence، specialist review و anecdote نوع‌های مختلف evidence هستند و قابل جایگزینی نیستند.
- Product-specific claim نیازمند exact product identity + official evidence + scoped specialist review است.
- Anecdote صرفاً signal است.
- شش محور product-doc investigation که PO از scope اجرای این roadmap خارج کرده، دوباره blocker این سند یا acceptance criteria نمی‌شوند.

## 6. Consultation routing
پیش از هر output:
1. Validate schema/source/confidence and conflicts.
2. Check required-data matrix.
3. Check safety/scope exclusions and specialist stop conditions.
4. Check evidence and knowledge status of dependent claim.
5. Evaluate candidate validity/ranking only if gates pass.
6. Return one of canonical response states; preserve conditionality and limits.
7. No execution-oriented instruction or consent inference.

### 6.1 Four motor states
- suggestion reviewable by specialist
- conditional suggestion, with named condition
- request more information
- stop/referral with reason

### 6.2 Five consultation response states
- suggestion reviewable by specialist
- needs more information or test
- needs in-person/specialist review
- safety stop — no execution suggestion
- outside first-version scope

Conditional suggestion is motor state, not a sixth response state.

## 7. Option rules
Only valid evidence-backed candidates can be presented. Invalid, rejected, unvalidated, evidence-less, duplicate, conflicting or rank-conflicted candidates are excluded or cause bundle suppression according to gate. At most three valid options; do not truncate a four-valid-option conflict to three. If only one valid option exists, present one; never manufacture alternatives. Rank by documented goal fit and technical validity, not preference alone.

## 8. Workflow and client-decision controls
Case workflow states: incomplete acceptance; awaiting evaluation; awaiting test; safety stopped; ready for specialist decision; awaiting client confirmation; approved for execution; in execution; needs follow-up; closed.

Client question ≠ acceptance. Acceptance ≠ execution consent. Separate records for suggestion version, acceptance, execution consent, specialist review, and performed steps.

- Rejected suggestion cannot return active.
- Changed target creates new version/full fresh evaluation; affected effective data changes invalidate dependent outputs only, unless dependency unknown → fail closed.
- Client stop request is recorded; only performed steps are recorded; no auto-resume.
- Restart, if permitted, requires fresh version and checks of current hair state/data/safety/rules/evidence.
- Changed data do not carry acceptance, consent, or specialist review automatically.

## 9. Specialist-review status
۱۵ topics in Activity 36 inventory and package in Activity 37. Actual specialist delivery has not occurred. Activity 38 defines review record schema; Activity 39 defines correction gate. Therefore all topics remain pending unless actual review records and evidence ledger later reconcile. No specialist approval is invented.

## 10. Corrections and release authority
A correction requires topic/description, specialist record ref, evidence refs, accepted scope, explicit PO approval/ref, scope note, baseline and target versions. Applied state requires trace receipt. Specialist approval is not PO acceptance; PO acceptance is not execution authorization.

## 11. Explicitly prohibited claims/behavior at this stage
- Exact result/formula from a single photo.
- Inferring porosity, structure, pigment or chemical history from image alone.
- Assuming same chemistry from similar code/brand/shade.
- Generalizing owner rule to other brands/series/code ranges.
- Treating anecdote as general rule.
- Guessing without reliable evidence.
- Treating prior safe use or a negative test as future safety guarantee.
- Treating data-complete intake as feasibility or recommendation approval.
- Publishing suggestion on internal engine failure or invalid/conflicting gate.
- Carrying acceptance/consent/review to a changed version.

## 12. Readiness summary
| Area | Status |
|---|---|
| Conceptual architecture and domain contracts | Documented; not merged |
| Owner-defined rules | Recorded with scope |
| Catalog identity structure | Recorded; not chemistry validated |
| Intake/target/history/regional data structures | Draft implementation branches; tests not run |
| Evidence audit and specialist review | Pending actual evidence/review |
| Corrections | Gate exists; no corrections applied |
| Runtime integration | Not verified |
| Test/CI | Not executed in this work sequence |
| Production/customer use | Not authorized |

## 13. Source documents in this roadmap
Foundation activities 2–6; catalog activities 7–11; intake/consultation activities 12–39. See individual docs and PRs for source/version traceability. This synthesis does not replace the individual records.
