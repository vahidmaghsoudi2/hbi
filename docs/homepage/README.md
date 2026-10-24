# HBI Homepage — menu map and operational documentation hub

**Status:** Documentation hub for homepage menus (updated 2026-10-24). Files here do not by themselves change production code, schema, API, or database.

## Start here

- **[مدیریت محصولات — قالب ورود پوست V1](product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md)** — قالب‌های ثابت تکمیل هوشمند زیر لاین پوست
- **[هاب مدیریت محصولات](product-management/README.md)** — فضای ثابت منوی مدیریت محصولات
- **[Canonical menu structure](menu-structure.json)** — دادهٔ ساختار منو
- **[Open prototype source](index.html)** — شبیه‌ساز مستنداتی
- [Operational roadmap](ROADMAP.md)
- [User-path checklist](USER_PATH_CHECKLIST.md)

## Authority map

| Location | Responsibility |
|----------|----------------|
| **[Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) body** | Sole authority for product decisions, permissions, Gates |
| **`docs/homepage/`** | Homepage menu map and operational docs |
| **`docs/homepage/product-management/`** | Product management menu: intake templates, field maps |
| **`docs/homepage/encyclopedia/`** | Encyclopedia menu registers (if present on branch) |
| **[PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)** | Product Knowledge research workbook only |

### Rules

1. Do not scatter homepage/product-intake operational specs outside `docs/homepage/` (and the matching submenu folder).
2. Do not record new PO policy decisions only in files; put them in Issue **#406** and link from the relevant folder.
3. Encyclopedia is not the system of record for product intake fields.
4. No file here alone authorizes schema/API/DB changes.

## Main menu (program homepage)

1. خانه و داشبورد  
2. مشتریان  
3. مشاوره  
4. فروش  
5. **مدیریت محصولات** → [product-management/](product-management/)  
6. کالا و موجودی  
7. خرید  
8. حسابداری و گزارش‌ها  
9. دانشنامه (در صورت فعال بودن در UI)

## Existing records (linked, not moved)

- [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406)
- [PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)
