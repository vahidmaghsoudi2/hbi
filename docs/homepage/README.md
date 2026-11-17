# HBI Homepage — menu map and operational documentation hub

> ## تصمیم الزام‌آور Product Owner — 2026-11-17
> **[HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001](../03_decision_log/HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001.md)**  
> دانشنامه بانک اصلی دانش مشاوره است.  
> تفسیر قدیمی «دانشنامه فقط مرجع انسانی/نمایشی است و در مسیر مشاوره نقشی ندارد» **منسوخ و غیرقابل استناد** است.  
> مدل هدف: `دانشنامه تأییدشده → Evidence → ProductKnowledge → Consultation`

**Status:** Documentation + editable prototype. The production homepage «دانشنامه» menu was implemented in [PR #441](https://github.com/vahidmaghsoudi2/hbi/pull/441); its nested skin navigation was finalized in merged [PR #489](https://github.com/vahidmaghsoudi2/hbi/pull/489). This documentation/prototype does not itself change application code, schema, API, or database.

## Start here

- **[View interactive menu preview](https://htmlpreview.github.io/?https://github.com/vahidmaghsoudi2/hbi/blob/docs/homepage-operational-folder-20261023/docs/homepage/index.html)** — opens the prototype in a static preview service.
- **[Open prototype source](index.html)** — HTML source stored in this repository.
- **[Canonical observed menu structure](menu-structure.json)** — editable source data used by the prototype.
- [Operational roadmap](ROADMAP.md) — completion stages and evidence gates.
- [User-path checklist](USER_PATH_CHECKLIST.md) — observed user paths and test evidence slots.
- **[مدیریت محصولات — قالب ورود پوست V1](product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md)** — fixed skin intake templates (canonical under homepage)
- **[هاب مدیریت محصولات](product-management/README.md)** — product-management menu documentation space
- **[دانشنامه — مرجع مستندات](encyclopedia/README.md)** — هاب هفت زیرمنو و مسیرهای محتوایی دانشنامه
- **[دانش پوست — فهرست محصولات](encyclopedia/skin/PRODUCTS.md)** — دفتر مرکزی نمونه‌ها و تغییرات محتوای دانش پوست
- **[دانشنامه ← رنگ مو — مرجع اصلی پروژه](encyclopedia/hair-color/README.md)** — هدف، تصمیم‌ها، قرارداد مشاوره، نقشهٔ دسترسی، وضعیت و گام بعدی؛ تغییرات فعلی در PR #542 و هنوز ادغام‌نشده
- **[تصمیم الزام‌آور دانشنامه](../03_decision_log/HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001.md)** — بانک اصلی دانش مشاوره؛ تفسیر display-only منسوخ است

> The prototype edits only a browser-local draft. To persist changes in the repository, export the JSON, review it, then submit the revised `menu-structure.json` through a Pull Request. The prototype does not write to GitHub automatically. The interactive preview uses a third-party static preview service and is not GitHub Pages or a production deployment. `menu-structure.json` remains the canonical menu data; the embedded fallback in `index.html` must be refreshed whenever that JSON changes.

## Authority map

| Location | Responsibility |
|----------|----------------|
| **[Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) body** | Sole authority for product decisions, permissions, Gates, and the official index of related IDs for Product Characteristics / homepage policy |
| **[HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001](../03_decision_log/HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001.md)** | Binding PO decision: دانشنامه is the primary knowledge base direction for consultation |
| **`docs/homepage/`** | Homepage menu map, prototype, operational docs and user-path evidence |
| **`docs/homepage/product-management/`** | Product management menu: skin intake template map (V1) |
| **[PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)** and its research files | Technical evidence and Product Knowledge research workbook |
| **Problem Space / PR #433 / P01–P61** | Content remains in its specialist registry; «دانش پوست → مشکلات پوستی» links to the existing Workspace Index without copying records |

### Rules that prevent another source-of-truth problem

1. Do not record new Product Owner decisions in this folder. Decisions and permissions belong in Issue **#406** and formal decision-log records; link to them here.
2. Do not create a second decision/status register.
3. Historical Issues/comments remain in GitHub; this hub links to them rather than pretending to move their history.
4. Menu labels marked `observed` are derived from `frontend/src/pages/NewHomePage.tsx`; the «دانشنامه» menu is active after PR #441. The prototype documents the menu and is not proof of any behavior beyond the source and runtime checks.
5. No file here authorizes production code, schema, API, database, product creation, QA, or activation changes by itself.
6. Skin intake template specs live only under `docs/homepage/product-management/`; do not scatter copies.
7. Do **not** cite older homepage language that treated دانشنامه as merely human-readable/display-only. That interpretation is superseded by HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001.

## Observed main menu

The current `NewHomePage.tsx` snapshot shows nine main menu cards:

1. خانه و داشبورد
2. مشتریان
3. مشاوره
4. فروش
5. مدیریت محصولات → [product-management/](product-management/)
6. کالا و موجودی
7. خرید
8. حسابداری و گزارش‌ها
9. دانشنامه

The prototype also identifies the top actions separately. «تنظیمات» is not treated as an active main-menu card because it is not present among those nine cards in the inspected source snapshot.

## Active encyclopedia menu — implementation and source-of-truth boundaries

The «دانشنامه» menu and its seven submenus are present in the production homepage after [PR #441](https://github.com/vahidmaghsoudi2/hbi/pull/441). The current second-level path is **دانشنامه → دانش پوست → (ویژگی محصولات پوستی | مشکلات پوستی)**. «ویژگی محصولات پوستی» opens the product encyclopedia surface (strategic primary knowledge base per HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001; runtime decision path still flows through Evidence/ProductKnowledge until the binding connection is implemented) and links to [PRODUCTS.md](encyclopedia/skin/PRODUCTS.md), containing the seven research dossiers P1–P7. «مشکلات پوستی» opens the existing [SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md](../product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md), whose canonical list is P01–P61. These remain two independent content registries; the menu is navigation only and must not copy either dataset. Their documented relationship source is the existing ProductProblemLink model/API; this navigation change does not add live relationship rendering to the UI. The other six encyclopedia destinations remain unchanged.

Two boundaries are explicit: «دانش مو» covers general hair/scalp knowledge, while «رنگ مو» covers coloring and care of color-treated hair. The knowledge category «سایر» is not the product-line value `OTHER`.

The menu implementation is merged; this does not claim that the six not-yet-created destination pages are operationally ready.

## Existing records (linked, not moved)

- [Issue #406 — decisions and Gates](https://github.com/vahidmaghsoudi2/hbi/issues/406)
- [HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001](../03_decision_log/HBI-PO-DEC-ENCYCLOPEDIA-PRIMARY-KB-001.md)
- [PR #411 — Product Knowledge research workbook](https://github.com/vahidmaghsoudi2/hbi/pull/411)
- [HBI operational roadmap](../HBI_HOME_OPERATIONAL_ROADMAP.md)
- [Homepage architecture decision](../HBI_HOME_PAGE_ARCHITECTURE_DECISION.md)
- [Homepage completion ledger](../HOMEPAGE_COMPLETION_LEDGER.md)
- [Homepage IA audit, Stage 2](../HOMEPAGE_IA_AUDIT_STAGE2.md)
- [Home frontend/backend connections](../HOME_FRONTEND_BACKEND_CONNECTIONS.md)

## Continue

1. Use the prototype to organize menu labels and submenus; do not treat edits as production changes.
2. Keep the JSON schema/data coherent and review exported changes before committing them.
3. Record actual browser/test outcomes in `USER_PATH_CHECKLIST.md` only when supported by evidence.
4. Send policy/Gate decisions to Issue #406 and formal decision-log records; Product Knowledge evidence remains linked to PR #411.
5. This folder is documentation and prototype only; production behavior changes must be implemented and reviewed in application code.
6. Any new work on consultation quality must align with the encyclopedia-as-primary-knowledge-base decision and the path `دانشنامه → Evidence → ProductKnowledge → Recommendation`.
