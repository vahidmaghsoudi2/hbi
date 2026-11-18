> ## 🔴 HISTORICAL BASELINE / RECONCILIATION REQUIRED — READ FIRST
>
> **This document is a strategic vision proposal, not the current execution plan.** Its baseline `89bb72004f4d8740f24535a8f8a6de87f8b11eba` is stale; current master was verified at `cc7848e472b837746e99103ea94ff4bb28eb0c2b` on 2026-10-12. Do not copy old status, priority, scope, or next-action statements into current work without rechecking current master and accepted contracts.
>
> ### Section-by-section disposition (2026-10-12)
> - **KEEP AS STRATEGIC VISION ONLY:** §§1–4, 6–15, 18, 20–22. These express useful direction/governance; they do not prove implementation or authorize changes.
> - **§5 — UPDATE / SCOPE-LIMITED:** structured ingredients and product comparison remain possible strategic capabilities, **not automatic V1 requirements**. Any implementation requires demonstrated business need, a bounded work package, acceptance criteria, and explicit authorization.
> - **§16 — SUPERSEDED AS AN EXECUTION QUEUE:** its workstream ordering must not be used as the live task list. Use current reconciled work in Issue #278 and the current skin-consultation roadmap proposal in PR #348; validate against current master before acting.
> - **§17 — PARTIALLY SUPERSEDED:** do not reopen the Home Page design mission from this paragraph. The Home Page is already active/current and its acceptance checklist has later updates on master. Product Line, category, and menu continuity questions may still matter, but must be checked against current routes and the currently assigned product/menu work—not inferred from this old vision.
> - **§19 — NOT RECHECKED:** E-03 is described here as a separate PERFUME runtime mission. This document alone does not establish its present status; verify the current E-03 issue and evidence before reusing that instruction.
> - **Baseline and all historical “current” wording — SUPERSEDED:** the old SHA is a historical checkpoint, not current Reality evidence.
>
> ### Current authority and guardrails
> 1. The approved skin intake execution baseline remains `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md`; do not reopen approved decisions without contrary evidence and explicit PO direction.
> 2. Issue #278 is the consolidated skin Product Intake reconciliation/decision index. Its historical checkpoints still require SHA-aware interpretation.
> 3. PR #348 is a proposal for the skin consultation/intelligence roadmap and remains separate from this broad strategic vision; it is not implementation or merge authorization.
> 4. PRs #332, #334 and #345, and the merged #322 work, are later implementation evidence for their bounded scopes. They do not, by themselves, close G8 / Issue #283.
> 5. Preserve this document for traceability. Do not delete useful strategic context; do not treat it as the live operational checklist. No code, contract, or merge is authorized by this reconciliation.
>
> Links: [Issue #278](https://github.com/vahidmaghsoudi2/hbi/issues/278) · [PR #348](https://github.com/vahidmaghsoudi2/hbi/pull/348) · [Issue #283 / G8](https://github.com/vahidmaghsoudi2/hbi/issues/283) · [PR #345](https://github.com/vahidmaghsoudi2/hbi/pull/345)
>
> ---
>
# HBI — ابلاغ رسمی جهت جدید معماری و دستور مشورت یکپارچه

**از طرف: وحید مقصودی — Product Owner**  
**موضوع: تعیین جهت جدید بررسی معماری HBI و دستور مشورت گروه**  
**مبنای بررسی: Current Master @ `89bb72004f4d8740f24535a8f8a6de87f8b11eba`**

## 1. تصمیم اصلی

از این مرحله، مسیر بررسی و توسعه HBI بر اساس یک اصل روشن ادامه خواهد یافت:

> **HBI فعلی حفظ می‌شود، اما هیچ تصمیم، مدل، معماری یا پیاده‌سازی قبلی صرفاً به دلیل قدیمی بودن الزاماً ادامه پیدا نمی‌کند.**

- آنچه درست و با هدف نهایی HBI سازگار است → **KEEP**
- آنچه درست است ولی ناقص است → **COMPLETE**
- آنچه موجود است ولی با جهت نهایی سازگار نیست → **CHANGE**
- آنچه واقعاً وجود ندارد و برای هدف HBI لازم است → **BUILD**

این رویکرد به معنی بازطراحی HBI از صفر نیست. هدف این است که سرمایه موجود HBI با کمترین دوباره‌کاری، به HBI مطلوب و یکپارچه تبدیل شود.

## 2. تصویر مطلوب HBI

```
HBI Home
   ↓
Product Lines / Business Domains
   ↓
Catalog
   ↓
Product Introduction
   ↓
Product Understanding
   ↓
Product Knowledge
   ↕
Customer Profile / Need
   ↓
Consultation
   ↕
Inventory / Availability / Price
   ↓
Recommendation
   ↓
Sale
   ↓
Customer Experience / History
   ↓
Analysis
   ↓
Decision Support / Continuous Improvement
```

این تصویر در این مرحله **Vision معماری و کسب‌وکاری** است، نه Contract فنی. وضعیت هر قسمت باید جداگانه از Reality فعلی استخراج شود.

## 3. Product Intake در این Vision

> **Product Intake دروازه ورود محصول به چرخه شناخت محصول است؛ نه کل Product Knowledge و نه کل HBI.**

هدف Intake فقط ثبت چند فیلد اولیه نیست، بلکه فراهم کردن مسیر:

```
Product Introduction
        ↓
Product Understanding
        ↓
Product Knowledge
```

تعداد فیلدها از ابتدا مصنوعی ثابت نمی‌شود. هر اطلاعات جدید باید نقش مشخص داشته باشد:

```
Why needed?
Source?
Confidence / Status?
Where consumed?
```

هدف، «اطلاعات بیشتر» نیست؛ هدف، **شناخت بهتر و قابل استفاده محصول** است.

## 4. شناخت محصول

HBI مطلوب باید بسته به نوع محصول اطلاعات لازم برای شناخت و تصمیم‌گیری را مدیریت کند، از جمله:

- هویت محصول، برند، نام و Variant
- Size و شناسه‌ها
- طبقه‌بندی
- ترکیبات و مواد تشکیل‌دهنده
- کاربردها و ویژگی‌های عملکردی
- مزایا و ادعاها
- تناسب با نیازها
- محدودیت‌ها و اطلاعات ایمنی
- نحوه مصرف
- منابع اطلاعاتی
- سایر اطلاعات مورد نیاز

این فهرست محدود و نهایی نیست.

## 5. ترکیبات و مقایسه محصولات

**Ingredients / Composition** نباید صرفاً یک متن ذخیره‌شده باشد. در معماری مطلوب، اطلاعات ترکیبات باید در صورت نیاز برای شناخت محصول، مقایسه، بررسی تناسب با نیاز، مشاوره، توضیح پیشنهاد و تصمیم‌سازی قابل استفاده باشد.

HBI باید در مسیر تکامل خود بتواند محصولات را بر اساس اطلاعات معتبر با یکدیگر مقایسه کند.

## 6. Customer و Need

محصول نباید جدا از مشتری و نیاز او دیده شود:

```
Product
+
Customer
+
Need
```

Customer Profile و Need باید در صورت نیاز در Consultation، Recommendation، Purchase، Experience و History قابل استفاده باشند.

## 7. Consultation

Consultation یکی از نقاط اتصال اصلی HBI است و ممکن است هم‌زمان به این اطلاعات نیاز داشته باشد:

```
Customer Profile
+
Need
+
Product Knowledge
+
Evidence
+
Inventory
+
Availability
+
Price
+
Previous Experience
```

بخش‌های مختلف باید با حفظ مالکیت داده‌های خود، اطلاعات مورد نیاز مشاوره را در اختیار آن قرار دهند.

> **Integration به معنی ادغام مالکیت همه داده‌ها نیست.**

## 8. Recommendation

این سند **Recommendation موجود را لغو یا بازطراحی نمی‌کند**. هدف، تعیین جایگاه Recommendation در تصویر یکپارچه HBI است.

در Vision مطلوب، خروجی Recommendation باید برای انسان قابل فهم و توضیح باشد و از اطلاعات معتبر لایه‌های مربوط استفاده کند.

این موضوع به معنی لغو scoring یا ranking موجود نیست. هرگونه تغییر در منطق Recommendation در مرحله‌ای مستقل و با Contract و مأموریت مشخص بررسی خواهد شد.

## 9. فروش، تجربه مشتری و یادگیری

```
Customer
→ Need / Case
→ Consultation
→ Recommendation
→ Product
→ Sale
→ Customer Experience
→ History
→ Analysis
→ Decision Support
```

تجربه مشتری ارزشمند است، اما:

```
Customer Experience ≠ Product Truth
Commercial Success ≠ Product Truth
```

Learning در این مرحله الزاماً Machine Learning نیست:

```
Recorded Experience
→ Analysis
→ Insight
→ Controlled Decision Support
```

## 10. نقش هوش مصنوعی

AI در HBI یک **ابزار کمکی** است و می‌تواند برای استخراج اطلاعات، استخراج ترکیبات، نرمال‌سازی، تحقیق، مقایسه منابع، تشخیص اطلاعات ناقص، تهیه Research Draft، غنی‌سازی اطلاعات و کمک به اپراتور استفاده شود.

اما:

```
AI Output ≠ Evidence
Research Draft ≠ Evidence
AI Output ≠ Product Truth
AI Output ≠ Final Decision
```

AI باید توانایی HBI را افزایش دهد، نه اینکه جایگزین سازوکار حقیقت و تصمیم‌گیری آن شود.

## 11. مرز اطلاعات

```
User / Operator Input
        ↓
AI Output / Extraction
        ↓
Research Draft
        ↓
Evidence
        ↓
Product Knowledge
        ↓
Decision Support
```

این لایه‌ها می‌توانند مرتبط باشند، اما معنای آنها نباید مخلوط شود.

همچنین:

```
Customer Experience ≠ Product Truth
Commercial Data ≠ Product Truth
Manufacturer Claim ≠ Automatically Verified Evidence
```

## 12. Reality قبل از Implementation

هیچ بخش جدیدی صرفاً بر اساس Vision این سند ساخته نمی‌شود.

برای هر ادعای مربوط به وضعیت موجود، شواهد باید تا حد امکان شامل:

```
File
+
Symbol / Route / Model / Section
+
Test
+
Commit / SHA
+
Runtime Evidence در صورت نیاز
```

باشد.

اصل:

```
Documented ≠ Implemented ≠ Runtime Proven
```

مبنای اصلی وضعیت فعلی، **Current Master و شواهد متناظر با آن** است.

## 13. Vision و Reality

**Reality** یعنی آنچه اکنون واقعاً در HBI وجود دارد.

**Vision** یعنی آنچه HBI باید در نهایت به آن برسد.

> **Reality سقف Vision نیست و Vision جایگزین Reality نیست.**

ممکن است قابلیتی در Vision وجود داشته باشد که هنوز در کد نیست، یا قابلیتی در کد موجود باشد که در معماری مطلوب آینده نیازمند اصلاح باشد. هر دو حالت باید بدون پیش‌داوری ثبت شوند.

## 14. دستور مشورت گروه

ترتیب اجباری:

```
VISION
   ↓
CURRENT HBI REALITY
   ↓
RECONCILIATION
   ↓
REAL GAPS
   ↓
TARGET ARCHITECTURE
   ↓
IMPLEMENTATION PLAN
```

نه:

```
VISION
   ↓
طراحی یک HBI جدید
   ↓
کدنویسی
```

هیچ عضو گروه نباید بدون بررسی سرمایه موجود، معماری موازی ایجاد کند.

## 15. قالب پاسخ اعضا

### A — KEEP / Established

چه چیزی موجود و سازگار است؟

```
File:
Symbol:
Test:
SHA:
Runtime Evidence:
```

### B — COMPLETE / Partial

چه چیزی موجود ولی ناقص است؟

```
Existing:
Missing:
Evidence:
```

### C — CHANGE / Incompatible

چه چیزی موجود است ولی با جهت نهایی سازگار نیست؟

```
Current:
Conflict with Target:
Reason:
Proposed Change:
```

### D — BUILD / Missing

چه چیزی واقعاً وجود ندارد ولی برای هدف HBI لازم است؟

```
Missing Capability:
Business Reason:
Architectural Location:
Dependencies:
```

### E — Proposed Architecture

پس از چهار مرحله بالا، اگر نیاز بود:

```
Target:
Reason:
Dependencies:
Sequence:
```

## 16. دامنه اصلی این دور مشورت

### لایه اول — اجباری

- زنجیره Home → Product → Knowledge → Customer → Consultation → Recommendation → Sale → Experience
- ارتباط واقعی اجزای موجود
- وضعیت واقعی آنها روی Master فعلی

### لایه دوم — اجباری

- Product Intake به‌عنوان دروازه
- Product Understanding
- Product Knowledge
- Ingredients / Composition
- Evidence
- Research
- AI-assisted Intake / Enrichment
- Customer Profile / Need

### لایه سوم — برای بررسی تکمیلی

- Product Comparison
- Customer Experience Intelligence
- Learning / Decision Support
- تکامل توضیح‌پذیری Recommendation

این تقسیم‌بندی برای جلوگیری از پاسخ‌های پراکنده است، نه برای حذف موضوعات مهم.

## 17. Home / Product Lines / Category

در بررسی Reality باید تفاوت میان این مفاهیم حفظ شود:

```
Home Label
≠
Product Line
≠
Accounting Category
```

قبل از هر تصمیم اجرایی درباره منوها و ساختار نهایی، Mapping واقعی این مفاهیم باید از روی وضعیت موجود مشخص شود.

## 18. اسناد و سوابق قبلی

اسناد، قراردادها، تصمیم‌ها، تست‌ها و پیاده‌سازی‌های قبلی سرمایه و سابقه پروژه‌اند و باید بررسی شوند.

اما:

> **وجود سند ≠ اثبات وضعیت فعلی**

اولویت بررسی وضعیت فعلی:

```
Current Code
→ Tests
→ CI
→ Runtime Evidence where required
```

اسناد تاریخی برای درک تصمیم‌ها و مسیر قبلی ارزشمندند، اما جایگزین Evidence وضعیت فعلی نیستند.

## 19. E-03

این دستور مشورت معماری، جایگزین مأموریت مستقل E-03 نیست.

E-03 معیار مستقل خود را دارد:

```
Official Product Intake Path
        ↓
Real PERFUME Product
        ↓
Runtime
        ↓
Reproducible Evidence
```

نتیجه این مشورت به‌خودی‌خود اثبات Runtime برای E-03 محسوب نمی‌شود.

## 20. مرز این سند

این سند:

- Contract فنی نیست؛
- مجوز Implementation نیست؛
- مجوز ایجاد Model جدید نیست؛
- مجوز ایجاد API جدید نیست؛
- مجوز تغییر Product Intake نیست؛
- مجوز تغییر Recommendation نیست.

این سند **دستور رسمی مشورت و تعیین جهت معماری HBI** است.

پس از پایان مشورت، هر تغییر اجرایی باید بر اساس نتیجه واقعی بررسی، Scope و Contract مستقل داشته باشد.

## 21. خروجی مورد انتظار

در پایان این مرحله باید بتوانیم برای بخش‌های اصلی HBI تصویر روشنی داشته باشیم:

```
KEEP
COMPLETE
CHANGE
BUILD
```

و سپس:

```
Target Architecture
        ↓
Priority
        ↓
Contracts
        ↓
Implementation
        ↓
Tests / CI
        ↓
Runtime Verification
        ↓
Real Product Pilot
```

## 22. اصل نهایی HBI

هدف HBI ساخت مجموعه‌ای از ماژول‌های مستقل نیست.

هدف، ساخت یک سیستم یکپارچه است که بتواند:

> **محصول را بشناسد، مشتری و نیاز او را بشناسد، اطلاعات معتبر محصول را در اختیار مشاوره قرار دهد، شرایط واقعی مانند موجودی و قیمت را در تصمیم‌گیری وارد کند، پیشنهاد قابل توضیح ارائه دهد، نتیجه واقعی را ثبت کند و از تجربه‌های ثبت‌شده برای تصمیم‌های بهتر آینده استفاده کند.**

در این مسیر:

> **HBI فعلی حفظ می‌شود، اما HBI آینده به گذشته محدود نمی‌شود.**

معیار هر تصمیم جدید:

```
HBI Vision
+
Current Reality
+
Real Business Need
```

### دستور نهایی

**فعلاً از این سند هیچ کدنویسی جدیدی آغاز نشود.**

ابتدا Reality موجود بررسی و با Vision تطبیق داده شود.

خروجی این دور فقط باید نشان دهد:

```
What do we have?
What is usable?
What is partial?
What is incompatible?
What is genuinely missing?
What should the target architecture be?
```

پس از آن درباره Implementation تصمیم‌گیری خواهد شد.
