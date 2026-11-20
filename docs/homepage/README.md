# HBI Homepage — menu map and operational documentation hub

**Status:** This folder contains observed UI documentation and a proposed, PO-confirmed information-architecture target. The target is documentation only and is not yet implemented in the application. No code, schema, API, database, inventory, product or customer data is changed by this documentation.

## Start here

- [Canonical observed and proposed menu structure](menu-structure.json)
- [Operational roadmap](ROADMAP.md)
- [User-path checklist](USER_PATH_CHECKLIST.md)
- [مدیریت محصولات — هاب و ساختار هدف](product-management/README.md)
- [قالب‌های ورود پوست V1](product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md)
- [دانشنامه — مرجع حوزه‌های دانشی باقی‌مانده](encyclopedia/README.md)
- [دانش پوست — دفتر پژوهش هفت محصول](encyclopedia/skin/PRODUCTS.md)
- [دانشنامه ← رنگ مو — مرجع اصلی پروژه](encyclopedia/hair-color/README.md)

## Authority map

| Location | Responsibility |
|---|---|
| [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) | Product Owner decisions, permissions, gates and current product-management policy |
| `docs/homepage/` | Observed homepage menu, target information architecture, prototype and user-path documentation |
| `docs/homepage/product-management/` | Product-management structure and skin intake specifications |
| [PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411) | Product Knowledge research continuity and technical evidence |
| `docs/product-intake-knowledge-registry/` | Existing canonical skin-problem records and index P01–P61 |

Do not create a parallel decision register. Product Owner decisions remain in Issue #406; these files document navigation and operational structure.

## Current observed UI (not the target)

The last documented `NewHomePage.tsx` snapshot contains these nine main menu cards:

1. خانه و داشبورد
2. مشتریان
3. مشاوره
4. فروش
5. مدیریت محصولات
6. کالا و موجودی
7. خرید
8. حسابداری و گزارش‌ها
9. دانشنامه

The current UI snapshot and its existing submenu implementation are recorded as **observed** in `menu-structure.json`. Do not read an observed entry as approval of the future structure.

## PO-confirmed target: مدیریت محصولات

The target unifies product management and skin knowledge in one main **مدیریت محصولات** environment while preserving the nine observed main-menu cards until a separately authorized UI change. The nine cards are: خانه و داشبورد، مشتریان، مشاوره، فروش، مدیریت محصولات، کالا و موجودی، خرید، حسابداری و گزارش‌ها، دانشنامه.

- **کالا و ویژگی محصول:** «فهرست کالاها» نقطه ورود و فهرست مرجع این بخش است. ایجاد، ورود، تکمیل و ویرایش هر کالا از همان فهرست به پرونده واحد همان محصول می‌رسد؛ همه ویژگی‌ها و اطلاعات هویتی/پژوهشی در همان پرونده نگهداری می‌شوند. اطلاعات عملیاتی و موجودی همان کالا نیز باید در همان محیط قابل مشاهده باشد.
- **مشکلات پوستی:** دانش مشکلات پوستی و ارتباط ساختاریافته آن با ویژگی‌ها و محصولات.

Product characteristics are maintained in the dossier of the relevant product. There is no separate «ویژگی محصولات» knowledge menu or duplicated characteristics bank. Product-to-problem and problem-to-product navigation should be possible through structured relationships; the recommendation engine evaluates suitability against the customer's context.

The target menu must not expose «بررسی و تأیید QA» as a separate destination or post-PO gate. Removing that menu does not remove quality controls: identity and version verification, duplicate checks, source/Evidence traceability and readiness, completeness and conflict review, applicable skin-safety checks, and a QA/reviewer verdict remain part of preparation before the final PO decision. PO approval completes information acceptance and directly sets ACTIVE; no second activation or repeated acceptance gate follows it.

### Product and consultation eligibility rules

- Creating a Product Master DRAFT with zero inventory is permitted before final acceptance; it is a working record, not sellable stock or a consultation candidate.
- A Product Master DRAFT may be created before acceptance as a working record and deleted later if not pursued.
- Product Owner approval completes information acceptance and directly sets the product to `ACTIVE`; there is no separate manual `APPROVED → ACTIVE` step or post-approval QA gate.
- Stock-In is permitted only after PO approval; the current Stock-In path must reject DRAFT/unapproved products.
- A product with sellable inventory greater than zero automatically enters the set considered by consultation.
- The consultation engine, not a pre-filter, evaluates suitability for the current customer. It recommends a suitable product, excludes an unsuitable one with a reason, or reports uncertainty when information is insufficient.
- No separate manual activation for consultation is required.

The seven P1–P7 dossiers in `encyclopedia/skin/PRODUCTS.md` remain research dossiers. Their presence does not mean they have been accepted as ProductKnowledge or Product Master records.

## Non-skin knowledge areas

The six non-skin knowledge areas remain preserved and must not be deleted as part of this change:

- دانش مو
- دانش ادکلن
- رنگ مو
- آرایش
- ابزار
- سایر

Their final navigation placement is still an open design detail. Until that placement is explicitly decided and implemented, retain their existing access paths. The target must not silently discard them or imply that their destination pages are all operationally complete.

## Scope and implementation boundary

- `menu-structure.json` keeps **observed current UI** separate from the **proposed target**.
- The current homepage implementation is not changed by this documentation PR.
- No database, API, schema, runtime, stock, product lifecycle, ProductKnowledge or ProductProblemLink data is changed.
- No P1–P7 dossier is promoted automatically.
- Any runtime or data-model change requires its own explicit scope and authorization.

## Existing references

- [Issue #406 — decisions and permissions](https://github.com/vahidmaghsoudi2/hbi/issues/406)
- [PR #411 — Product Knowledge research workbook](https://github.com/vahidmaghsoudi2/hbi/pull/411)
- [Homepage architecture decision](../HBI_HOME_PAGE_ARCHITECTURE_DECISION.md)
- [Homepage completion ledger](../HOMEPAGE_COMPLETION_LEDGER.md)
- [Homepage IA audit, Stage 2](../HOMEPAGE_IA_AUDIT_STAGE2.md)
