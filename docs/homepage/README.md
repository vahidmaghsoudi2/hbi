# HBI Homepage — menu map and operational documentation hub

**Status:** Documentation + editable prototype only (2026-10-23). This is not the production homepage and does not change application code, schema, API, or database.

## Start here

- **[View interactive menu preview](https://htmlpreview.github.io/?https://github.com/vahidmaghsoudi2/hbi/blob/docs/homepage-operational-folder-20261023/docs/homepage/index.html)** — opens the prototype in a static preview service.
- **[Open prototype source](index.html)** — HTML source stored in this repository.
- **[Canonical observed menu structure](menu-structure.json)** — editable source data used by the prototype.
- [Operational roadmap](ROADMAP.md) — completion stages and evidence gates.
- [User-path checklist](USER_PATH_CHECKLIST.md) — observed user paths and test evidence slots.

> The prototype edits only a browser-local draft. To persist changes in the repository, export the JSON, review it, then submit the revised `menu-structure.json` through a Pull Request. The prototype does not write to GitHub automatically. The interactive preview uses a third-party static preview service and is not GitHub Pages or a production deployment. `menu-structure.json` remains the canonical menu data; the embedded fallback in `index.html` must be refreshed whenever that JSON changes.

## Authority map

| Location | Responsibility |
|----------|----------------|
| **[Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) body** | Sole authority for product decisions, permissions, Gates, and the official index of related IDs for Product Characteristics / homepage policy |
| **`docs/homepage/`** | Homepage menu map, prototype, operational docs and user-path evidence |
| **[PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)** and its research files | Technical evidence and Product Knowledge research workbook |
| **Problem Space / PR #433 / P01–P61** | Out of scope for this homepage workstream |

### Rules that prevent another source-of-truth problem

1. Do not record new Product Owner decisions in this folder. Decisions and permissions belong in Issue **#406**; link to them here.
2. Do not create a second decision/status register.
3. Historical Issues/comments remain in GitHub; this hub links to them rather than pretending to move their history.
4. Menu labels marked `observed` are derived from `frontend/src/pages/NewHomePage.tsx` on the recorded master snapshot. The prototype is an editable proposal surface, not proof that an added menu exists in production.
5. No file here authorizes production code, schema, API, database, product creation, QA, or activation changes.

## Observed main menu

The current `NewHomePage.tsx` snapshot shows eight main menu cards:

1. خانه و داشبورد
2. مشتریان
3. مشاوره
4. فروش
5. مدیریت محصولات
6. کالا و موجودی
7. خرید
8. حسابداری و گزارش‌ها

The prototype also identifies the top actions separately. «تنظیمات» is not treated as an active main-menu card because it is not present among those eight cards in the inspected source snapshot.

## Existing records (linked, not moved)

- [Issue #406 — decisions and Gates](https://github.com/vahidmaghsoudi2/hbi/issues/406)
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
4. Send policy/Gate decisions to Issue #406 and Product Knowledge evidence to PR #411.
5. No code change is authorized by this documentation PR.
