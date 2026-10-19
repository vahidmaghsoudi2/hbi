# HBI — Independent Recommendation Factor Discovery (Team Aggregate)

**Location:** `08-Meeting-Room/MTG-REC-FACTORS-2026-09-08/`  
**Date recorded:** 2026-09-08  
**Mission stage:** Factor Discovery & Prioritization · then Round-2 critical synthesis  
**Rules:** No formula · No weight · No percentage · No implementation  
**Gallery scope:** Offline HBI Gallery / Inventory (not global market search)

```
Customer Need → Available Products in HBI Gallery → Eligibility / Suitability → Recommendation
```

**Governance links:**
- Issue #37 — Recommendation Parameter Weighting (**OPEN / NOT AUTHORIZED**)
- ADR-REC-INPUT-001 — input semantics (separate)
- PR #36 — HOLD / DO NOT MERGE (not a precedent)
- Docs PR: #38

**How to participate:** append only your own section; do not overwrite others.

---

# PART A — Round 1: Independent factor lists (max 20 each)

---

## Member: Grok (xAI) — Independent list

1. **ایمنی و منع مصرف** — تضاد با ریسک/آلرژی/محدودیت مشتری، قبل از هر رتبه‌بندی کیفی  
2. **تناسب نیاز–اندیکاسیون** — تطابق نیاز/وضعیت مشتری با کاربرد مشروع محصول  
3. **Ingredients و تناسب فرمولاسیون** — مادهٔ مؤثر و فرم مناسب نیاز (نه ادعای بازاریابی)  
4. **کیفیت شواهد مرتبط با همان نیاز** — Evidence تأییدشده برای منافع واقعاً مرتبط  
5. **اعتماد به سابقهٔ محصول (Identity / QA)** — رکورد قابل اتکا برای توصیه  
6. **محدودیت‌های پروفایل مشتری** — پوست/مو/پوست سر و مشابه  
7. **کامل بودن Product Knowledge برای مشاوره** — دادهٔ کافی برای توجیه عملی توصیه  
8. **موجودی قابل فروش در HBI** — واقعیت آفلاین؛ در دسترس نبودن = محدودیت eligibility  
9. **تعارض شواهد / نقض مرز ادعا** — conflict یا claim نامعتبر  
10. **علائم منع و کنارگذاری در دانش محصول**  
11. **تجربهٔ اپراتور/فروشنده (محلی و ساخت‌یافته)** — سیگنال، نه جایگزین Evidence  
12. **الگوی فروش–مرجوعی برای پروفایل مشابه** — فقط اگر دادهٔ محلی قابل اتکا باشد  
13. **دسترس‌پذیری اقتصادی برای زمینهٔ مشتری** — قید عملی، نه امتیاز کیفیت  
14. **اعتبار برند/رگولاتوری فقط وقتی به ایمنی یا اصالت مربوط است**  
15. **بازخورد رضایت مصرف‌کننده (اگر حاکمیتی و محلی باشد)**  
16. **پروکسی تکرار خرید / پذیرش (اگر وجود داشته باشد)** — ضعیف و فرعی  
17. **محبوبیت بازار / روند** — تجاری؛ اولویت پایین برای مأموریت بالینی HBI  
18. **سیگنال شبکه‌های اجتماعی** — پرنویز؛ اولویت بسیار پایین  
19. **تأمین خارج از Gallery** — فقط Exception آینده، نه عامل رتبه‌بندی فعلی  
20. **تازگی یا کمپین تبلیغاتی** — پایین‌ترین  

---

## Member: Qwen-2 — Independent list

1. **موانع ایمنی و منع مصرف (Contraindications):** Gate مطلق، نه امتیاز  
2. **تطابق مستقیم نیاز با ماده مؤثره (Active Ingredient Match)**  
3. **پروفایل بیولوژیکی مشتری**  
4. **قدرت شواهد علمی (Evidence Strength)**  
5. **کیفیت و پایداری فرمولاسیون**  
6. **موجودی لحظه‌ای در گالری**  
7. **سابقه واکنش مشتری**  
8. **تأییدیه و مداخله اپراتور/متخصص**  
9. **سازگاری با روتین فعلی مشتری**  
10. **همخوانی با بودجه مشتری**  
11. **پذیرش حسی و آرایشی (Cosmetic Elegance)**  
12. **اعتبار بالینی برند**  
13. **بازخورد واقعی مصرف‌کنندگان در اکوسیستم HBI**  
14. **تازگی و تاریخ انقضا**  
15. **سهولت استفاده و پیچیدگی روتین**  
16. **هم‌افزایی سبد خرید (Cross-sell Synergy)**  
17. **ویژگی‌های اخلاقی و پایداری** — ترجیحی نه الزامی  
18. **روندهای محبوبیت بازار** — سیگنال ضعیف  
19. **پتانسیل تأمین استثنایی** — آینده  
20. **زیبایی بصری بسته‌بندی** — کم‌اهمیت‌ترین در سیستم مبتنی بر شواهد  

---

## Member: Grok-2 — Independent list

1. **ایمنی و منع مصرف**  
2. **تناسب با نیاز واقعی مشتری**  
3. **موجودی قابل‌فروش در Gallery**  
4. **هویت و وضعیت حاکمیتی محصول**  
5. **ترکیبات و فرمولاسیون واقعی**  
6. **کیفیت و نوع شواهد**  
7. **شدت و قطعیت شواهد برای همان ادعا**  
8. **ریسک تحریک، حساسیت و آسیب تجمعی**  
9. **قابلیت استفاده عملی در شرایط مشتری**  
10. **سابقه و زمینهٔ همان مشتری در HBI**  
11. **وضوح دانش محصول (Product Knowledge)**  
12. **قیمت و تناسب اقتصادی همان مراجعه**  
13. **تجربه و مشاهدهٔ اپراتور حضوری**  
14. **بازخورد و نتیجهٔ مصرف‌کنندگان قبلی همان محصول در HBI**  
15. **فروش و تکرار خرید واقعی همان گالری**  
16. **پایداری و اعتبار برند در حد همان دسته**  
17. **سازگاری با سبد پیشنهادی چندمحصولی**  
18. **تازگی، بچ و شرایط نگهداری مؤثر بر کیفیت**  
19. **سیگنال‌های بیرونی بازار و شبکهٔ اجتماعی**  
20. **تأمین خارج از موجودی به‌عنوان استثنا**  

---

## Member: Qwen-1 — Independent list

1. **ایمنی و منع مصرف** — Hard Gate  
2. **انطباق علمی ترکیبات با نیاز**  
3. **وضعیت موجودی قابل‌فروش**  
4. **قدرت و نوع منبع شواهد**  
5. **وضعیت تأیید کیفیت شواهد (QA Status)**  
6. **تضاد در شواهد (Evidence Conflict)**  
7. **اطمینان از دانش محصول**  
8. **پروفایل دقیق مشتری**  
9. **بازخورد و تجربه واقعی مصرف‌کننده**  
10. **سابقه و اعتبار برند**  
11. **قیمت و تناسب اقتصادی**  
12. **یادداشت‌ها و مداخله اپراتور**  
13. **سازگاری با روتین فعلی**  
14. **پیچیدگی دستور مصرف**  
15. **منطقه جغرافیایی و اقلیم**  
16. **نوع بسته‌بندی و بهداشت**  
17. **روندهای بازار و محبوبیت**  
18. **تازگی فرمولاسیون یا سری ساخت**  
19. **پتانسیل تأمین استثنایی**  
20. **پایداری زیست‌محیطی و اخلاقی**  

---

## Member: GPT-1 — Independent list

1. تناسب با نیاز واقعی مشتری  
2. ایمنی و منع مصرف  
3. ترکیبات و ویژگی‌های واقعی فرمولاسیون  
4. کیفیت و قدرت شواهد علمی  
5. شواهد اختصاصی محصول  
6. Product Knowledge ساختاریافته و معتبر  
7. وضعیت و کیفیت شواهد مربوط به ادعاها (Supported/Partial/Conflict/Unknown)  
8. مناسب‌بودن برای وضعیت پوستی/مویی مشتری  
9. تطابق با محدودیت‌ها و ترجیحات صریح مشتری  
10. موجودی و قابلیت فروش واقعی در HBI Gallery  
11. کیفیت داده و کامل‌بودن اطلاعات تصمیم  
12. Conflict بین شواهد، ادعاها یا اطلاعات مشتری و محصول  
13. تجربه و بازخورد واقعی مصرف‌کنندگان  
14. نتایج فروش واقعی محصول — سیگنال تجاری نه اثربخشی علمی  
15. تجربه و قضاوت اپراتور/فروشنده  
16. قیمت و تناسب اقتصادی  
17. اعتبار و ثبات برند/تأمین‌کننده  
18. رفتار و ترجیحات خرید مشتری  
19. روند زمانی و محبوبیت بازار  
20. Consumer/Social Signals — سیگنال کمکی نه شواهد علمی  

---

## Member: DeepSeek-1 — Independent list

1. **ایمنی / Contraindication** — Gate نه Weight  
2. **شرایط بالینی / Need Match**  
3. **شواهد علمی (Evidence Quality)**  
4. **وضعیت موجودی (Availability)**  
5. **تطابق با پروفایل مشتری**  
6. **ترکیبات مؤثر (Ingredients)**  
7. **عوارض جانبی شناخته‌شده**  
8. **برند و اعتبار تولیدکننده**  
9. **قیمت / مقرون‌به‌صرفه‌بودن**  
10. **بازخورد مصرف‌کنندگان**  
11. **تجربه فروشنده / اپراتور**  
12. **سابقه خرید مشتری**  
13. **روندهای بازار**  
14. **تازگی محصول**  
15. **وضعیت تاییدیه‌ها (QA/Regulatory)**  
16. **محصولات جایگزین**  
17. **فصل / شرایط محیطی**  
18. **ترجیحات شخصی مشتری**  
19. **شبکه‌های اجتماعی و Consumer Signals**  
20. **قابلیت ترکیب با سایر محصولات**  

---

## Member: Perplexity — Independent list

1. ایمنی و منع مصرف مشتری  
2. هدف مشخص مشتری در همین مراجعه  
3. صلاحیت و هویت محصول  
4. موجودی واقعی و قابل فروش  
5. شواهد معتبر درباره کاربرد محصول  
6. Conflictهای حل‌نشده  
7. کیفیت و استقلال Evidence  
8. سازگاری با شرایط خوداظهاری مشتری  
9. روش مصرف و قابلیت اجرای واقعی  
10. تجربه قبلی همان مشتری  
11. ترکیبات و هشدارهای واقعی محصول  
12. داده‌های Unknown، کهنه یا تأییدنشده  
13. ترجیحات صریح مشتری  
14. سازگاری با روتین فعلی  
15. ارزش اقتصادی برای همان مشتری  
16. تازگی و کیفیت فیزیکی کالا  
17. قابلیت توضیح توصیه (explainability)  
18. اولویت و تأیید انسانی فروشنده  
19. بازخورد بازار و مصرف‌کنندگان — offline فرعی  
20. محصول خارج از موجودی گالری — فعلاً نه Recommendation اصلی  

---

## Member: GPT-2 — Independent list

(Same structure as Grok-2 list submitted by PO — safety, need, inventory, identity, ingredients, evidence quality/strength, irritation risk, practical use, customer history, PK clarity, price, operator, local feedback, local sales, brand, multi-product basket, batch/storage, external signals, exception supply.)

1. ایمنی و منع مصرف  
2. تناسب با نیاز واقعی مشتری  
3. موجودی قابل‌فروش در Gallery  
4. هویت و وضعیت حاکمیتی محصول  
5. ترکیبات و فرمولاسیون واقعی  
6. کیفیت و نوع شواهد  
7. شدت و قطعیت شواهد برای همان ادعا  
8. ریسک تحریک، حساسیت و آسیب تجمعی  
9. قابلیت استفاده عملی در شرایط مشتری  
10. سابقه و زمینهٔ همان مشتری در HBI  
11. وضوح دانش محصول  
12. قیمت و تناسب اقتصادی همان مراجعه  
13. تجربه و مشاهدهٔ اپراتور حضوری  
14. بازخورد مصرف‌کنندگان قبلی همان محصول در HBI  
15. فروش و تکرار خرید واقعی همان گالری  
16. اعتبار برند در حد همان دسته  
17. سازگاری با سبد چندمحصولی  
18. تازگی، بچ و نگهداری  
19. سیگنال‌های بیرونی بازار و سوشال  
20. تأمین خارج از موجودی به‌عنوان استثنا  

---

## Member: DeepSeek-2 — Round 1 note

Round 1 submission was mission/ops acknowledgment only — **no 20-factor list**. Recorded as such.

---

# PART B — Round 2: Independent critical synthesis (after reading the aggregate)

*Still no Weight / Percentage / Formula / Implementation. Issue #37 remains OPEN.*

---

## Synthesis: Member A (conceptual separation focus)

1. Safety/contraindication is foundational; several views treat it as Hard Gate — must not be leveled with preference factors.  
2. Real need–product fit is repeated almost everywhere — core of Recommendation.  
3. Sellable Gallery inventory is stably repeated — “is it even a practical option?” not mere product quality.  
4. Real ingredients vs marketing claims must stay separated.  
5. “Evidence Quality” in the file mixes strength, source type, QA, product-specificity, claim/need linkage — do not treat as one factor yet.  
6. Evidence Conflict is not merely weak evidence — different nature.  
7. Product Identity/QA/Governance must not merge with Evidence Quality or Brand.  
8. Customer Profile ≠ Need Match — context vs relationship to this visit’s goal.  
9. Contraindication ≠ irritation risk — absolute barrier vs different risk character.  
10. Routine Compatibility ≠ Practical Usability — both matter, not interchangeable.  
11. Historical customer response ≠ consumer feedback ≠ sales/repeat — three different concepts.  
12. Operator experience is repeated but must not replace Evidence.  
13. Price is practical context constraint more than product-quality signal.  
14. Brand is over-elevated in some lists; must not replace Identity/QA/Evidence.  
15. Trends/popularity/social are weak/noisy/commercial — over-highlighted relative to value.  
16. Packaging beauty, cross-sell, sustainability are peripheral vs decision core.  
17. Gap: Explainability (strong in Perplexity) underweighted elsewhere — matters for HBI operator+customer.  
18. Gap: Decision-data completeness quality ≠ Evidence Quality (GPT-1 / Perplexity).  
19. Observation only: Safety/Inventory/Eligibility often spoken as Gate/Filter; Operator/Consumer/Sales/Trends as Signal.  
20. Revision: do not treat need_match / evidence_score / inventory_score as the whole factor space; first clarify Eligibility vs Evidence vs Customer Context vs Practical Constraints vs Signals.

---

## Synthesis: Grok-2 → PO

1. Truly important: safety, need this visit, sellable inventory, product governance identity, real ingredients, evidence quality (not mere row existence).  
2. Strong team repeats: safety, need, inventory, evidence, ingredients, profile, price, operator, consumer feedback, brand, out-of-stock exception as future-only.  
3. Medium repeats: evidence CONFLICT, UNKNOWN/incomplete data, routine compatibility, sensory/texture, batch freshness, local gallery sales.  
4. Over-elevated in some lists: brand near top; market/social mid-rank; FDA/ISO labels without offline data reality.  
5. Underweighted: Gate vs Score separation in lists themselves; explainability to customer; multi-product layering; reserved vs displayed stock; weak Persian text need↔product matching.  
6. Must not co-class: safety≠rank score; zero stock≠“low priority”; manufacturer claim≠independent evidence; sales≠efficacy; operator≠unverified fact; social trend≠science.  
7. Self-revision: inventory and identity stay near each other, both before “evidence score,” closer to **entry filters** than competitors of need_match.  
8. Role observation only: safety, hard CONFLICT, unsellable, invalid identity → Gate/Filter candidates; need + claim-linked evidence → later rank candidates; UNKNOWN → confidence modifier not invented number; operator/local sales/brand/social → signals.  
9. Method risk: near-duplicate lists weaken independence — next stage should weight **differences** and unique factors.  
10. Offline constraint largely respected.  
11. Evidence strength often conflated with Product Knowledge — keep separate.  
12. HBI-local consumer feedback ≠ public internet reviews.  
13. Price matters but below safety/need/inventory.  
14. No one assigned weights this round — healthy.  
15. Soft consensus: safety + need + inventory + identity + ingredients/evidence; main dispute: brand, trends, operator, inventory-as-gate vs rank.  
16. Next input observation: factor × probable-role matrix before any weighting.  
17. Proposed gap factor: “Is the recommendation defensible and uncertainty-bounded in front of the customer?”  
18. Underweighted: systemic drug/condition interactions beyond skin type if in profile.  
19. No weighting decision taken.  
20. Ready for Gate/Filter/Signal/Candidate-Weight discussion without implementation.

---

## Synthesis: Member B (clinical emphasis)

1. Safety must be absolute **Gate**, not compensable score.  
2. Active-ingredient-to-need match is clinical core — Candidate Weight observation.  
3. Evidence strength for specific claims — Candidate Weight observation.  
4. Customer profile limits (skin/hair/scalp) — Gate/Filter observation.  
5. Inventory and customer budget should not enter ranking formula — pre-score **Filters** (observation).  
6. Operator experience and sales-return sometimes over-elevated — weak **Signals** in evidence-based system.  
7. Cross-product interaction underweighted — important gap.  
8. Formulation chemical stability (e.g. pH interactions) vital but missing.  
9. Brand/regulatory only when tied to safety or authenticity.  
10. Local governed consumer feedback / repurchase can be valid **Signal**.  
11. Market popularity / social = noisiest signals.  
12. Exception sourcing not a current ranking factor.  
13. Self-revision: packaging beauty should be **out of scope** for clinical recommender, not rank 20.  
14. Novelty/campaign correctly lowest — weak commercial signal.  
15. Evidence conflict / claim-boundary violation — Gate or severe suppressor observation.  
16. Product Knowledge completeness is precondition, not independent score factor.  
17. Never merge Filter (inventory) with Weight (evidence quality) in one computational bucket.  
18. Note on aggregate status: earlier incomplete views of file corrected by full multi-member content.  
19. Governance: no percentages/formulas this stage.  
20. Next stage should formally define Gate/Filter/Signal/Weight boundaries in writing.

---

## Synthesis: DeepSeek-2 (after reading full aggregate)

1. Safety/contraindications — top or absolute Gate in all lists.  
2. Sellable inventory — eligibility condition in most lists.  
3. Need ↔ active/formulation match — recommendation core in most lists.  
4. Evidence strength — quality criterion across all lists.  
5. Customer profile personalization — widely repeated.  
6. Identity/QA governance — repeated in several lists.  
7. Evidence conflict — separate in multiple lists.  
8. Operator experience — repeated; not Evidence substitute.  
9. Consumer feedback / repurchase — common secondary.  
10. Price — common practical factor.  
11. Over-elevated: market trends, social signals, packaging beauty, exception sourcing.  
12. Gaps: explainability (mostly Perplexity); regional/climate (Qwen-1); season (DeepSeek-1); alternatives (DeepSeek-1); multi-product synergy (Grok-2/GPT-2).  
13. Must separate: safety vs quality score; inventory vs effectiveness; consumer feedback vs clinical evidence; market trend vs need match.  
14. Self-revision: drops “impact on products A–D” from recommendation-priority space → change-management domain.  
15. Role observation table submitted as **observation only** (Gate candidates: safety, inventory, identity; quality signals: evidence, need, ingredients, profile, conflict; weaker weight candidates: price, feedback, operator, brand…; future candidates: explainability, regional, cross-sell).  
16. Confirms no weight/percentage/formula decision.  
17. PR #38 viewed as documentation-only, low risk.  
18. Issue #37 must stay OPEN.  
19. Round-1 had no DeepSeek-2 factor list — now Round-2 synthesis filled.  
20. Awaits PO for formal Gate/Filter/Signal/Weight phase.

---

## Synthesis: Grok (this chat) — Round 2

1. Important: safety, real need this visit, claim-linked evidence, real ingredients/formulation, product identity/QA, sellable inventory.  
2. Strong repeats across team: safety, need, inventory, evidence, ingredients, profile, operator, price, brand, social/trends at bottom.  
3. Over-elevated: brand-as-near-core; trends/social mid-list; packaging aesthetics inside clinical rank space.  
4. Underweighted gaps: explainability; decision-data completeness ≠ evidence quality; cumulative multi-product risk; reserved vs sellable stock.  
5. Do not co-bucket: safety with quality rank; inventory access with scientific goodness; brand with evidence; local HBI feedback with internet noise.  
6. Do not co-bucket: semantic need match with token/string heuristics.  
7. Self-revision vs earlier list: inventory slightly higher for offline path; incomplete PK more as confidence limiter than safety/need substitute.  
8. Role observation only: safety, identity/QA, unsellable, hard conflict → Gate/Filter candidates; linked evidence + ingredient fit + profile fit → later score candidates; operator/local sales/price/brand → Signal/Constraint candidates.  
9. Method note: near-duplicate member lists reduce independence signal — next phase should stress disagreements and unique factors.  
10. Soft consensus real on safety–need–evidence–ingredients–inventory; dispute on brand, trends, operator, inventory-as-gate.  
11. Evidence concepts must be split before any scoring policy: source type ≠ QA ≠ conflict ≠ claim linkage.  
12. Profile ≠ need match (agree with Member A).  
13. Historical self response ≠ peer feedback ≠ commercial sales.  
14. Exception out-of-gallery supply remains non-ranking for current phase.  
15. No weights, percentages, formulas, calculate() changes, or ranking decision.  
16. Issue #37 stays OPEN.  
17. Value of this stage: conceptual separation > premature numbers.  
18. Ready for PO-led comparison of all Round-2 syntheses.  
19. Still forbid promoting PR #36 heuristics to HBI rules.  
20. Next useful artifact (when PO orders): factor × role-hypothesis matrix — still not weights.

---

## Aggregate status

| Artifact | Status |
|----------|--------|
| Round-1 factor lists | Recorded |
| Round-2 syntheses | Recorded (this commit) |
| Official Gate/Filter/Signal/Weight decision | **NOT MADE** |
| Issue #37 Weighting | **OPEN** |
| Implementation / calculate() | **UNTOUCHED** |
