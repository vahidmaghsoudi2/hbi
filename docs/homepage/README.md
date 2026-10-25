# HBI Homepage — menu map and operational documentation hub

**Status:** Documentation hub for homepage menus (updated 2026-10-24). Files here do not by themselves change production code, schema, API, or database.

## Start here

- **[دانشنامه — مرجع مستندات](encyclopedia/README.md)** — منو و هفت زیرمنو؛ محل ثبت محتوا و تصمیم‌های هر زیرمنو
- **[دانش پوست — فهرست محصولات](encyclopedia/skin/PRODUCTS.md)** — نمونه‌ها + قالب افزودن/ویرایش/حذف از دانشنامه
- **[قالب‌های آمادهٔ ورود محصول پوستی V1](https://github.com/vahidmaghsoudi2/hbi/blob/master/docs/homepage/product-management/SKIN_INTAKE_TEMPLATE_FORMS_V1.md)** — نه قالب مصوب، باکس‌های مشترک و اختصاصی، قواعد منبع و معیارهای پذیرش تست
- **[Canonical menu structure](menu-structure.json)** — دادهٔ ساختار منو
- **[Open prototype source](index.html)** — شبیه‌ساز مستنداتی
- [Operational roadmap](ROADMAP.md)
- [User-path checklist](USER_PATH_CHECKLIST.md)

## Authority map

| Location | Responsibility |
|----------|----------------|
| **[Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) body** | Sole authority for product decisions, permissions, Gates |
| **`docs/homepage/`** | Homepage menu map, operational docs |
| **`docs/homepage/encyclopedia/`** | Encyclopedia menu + per-submenu registers (skin products, decisions) |
| **[PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)** | Product Knowledge research workbook |
| **Problem Space / P01–P61** | Specialist registry under `docs/product-intake-knowledge-registry/` — not duplicated here |

### Rules

1. Do not record new Product Owner product-policy decisions only here; put them in Issue **#406** and link from the relevant submenu folder.
2. Do not create a parallel decision register outside this map + #406.
3. Encyclopedia **main submenus are permanent**; only product/content rows inside a submenu are added, edited, or removed from the encyclopedia list.
4. No file here alone authorizes schema/API/DB changes.

## Main menu (program homepage)

1. خانه و داشبورد  
2. مشتریان  
3. مشاوره  
4. فروش  
5. مدیریت محصولات  
6. کالا و موجودی  
7. خرید  
8. حسابداری و گزارش‌ها  
9. **دانشنامه** → [encyclopedia/](encyclopedia/)

## Encyclopedia submenus

| Submenu | Docs |
|---------|------|
| دانش پوست | [encyclopedia/skin/](encyclopedia/skin/) |
| دانش مو | [encyclopedia/hair/](encyclopedia/hair/) |
| دانش ادکلن | [encyclopedia/perfume/](encyclopedia/perfume/) |
| رنگ مو | [encyclopedia/hair-color/](encyclopedia/hair-color/) |
| آرایش | [encyclopedia/makeup/](encyclopedia/makeup/) |
| ابزار | [encyclopedia/tools/](encyclopedia/tools/) |
| سایر | [encyclopedia/other/](encyclopedia/other/) |

## Existing records (linked, not moved)

- [Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406)
- [PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)
