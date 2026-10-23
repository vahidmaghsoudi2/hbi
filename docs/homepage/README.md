# HBI Homepage — operational documentation hub

**Status:** Skeleton only (2026-10-23). Documentation PR; no application code, schema, API, UI, or database changes.

**Purpose:** Single folder for **operational** homepage documentation (user paths, checklists, execution notes). This folder is **not** a product-decision register.

## Authority map (locked)

| Location | Responsibility |
|----------|----------------|
| **[Issue #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) body** | Only place for product decisions, permissions, Gates, and the official index of related IDs for Product Characteristics / homepage policy |
| **`docs/homepage/` (this folder)** | Operational docs only: how the homepage is used/tested, checklists, links to evidence |
| **[PR #411](https://github.com/vahidmaghsoudi2/hbi/pull/411)** and related research files | Technical evidence and Product Knowledge research workbook |
| **Problem Space / PR #433 / P01–P61** | **Out of scope** for this folder |

### Explicit rules

1. Do **not** record new PO decisions in this folder. Decisions go in Issue **#406** body; this folder may **link** to them.
2. Do **not** create `DECISIONS_AND_STATUS.md` here (rejected: risk of a second decision SSOT).
3. Historical Issues/comments are not moved; reference them by URL from this hub.
4. Files here never authorize code, schema, API, UI, DB, product create, QA, or activation.

## Files in this folder

| File | Role |
|------|------|
| [README.md](README.md) | This hub: authority map, links, how to continue |
| [ROADMAP.md](ROADMAP.md) | Operational stages and acceptance criteria for homepage completion work |
| [USER_PATH_CHECKLIST.md](USER_PATH_CHECKLIST.md) | Real user path steps and test evidence slots |

## Related existing docs (not moved; linked only)

These already live under `docs/` on `master`. This hub does not replace or delete them:

- `docs/HBI_HOME_OPERATIONAL_ROADMAP.md`
- `docs/HBI_HOME_PAGE_ARCHITECTURE_DECISION.md`
- `docs/HOMEPAGE_COMPLETION_LEDGER.md`
- `docs/HOMEPAGE_IA_AUDIT_STAGE2.md`
- `docs/HOME_FRONTEND_BACKEND_CONNECTIONS.md`

## Current operational status (one line)

Homepage operational completion is **in progress / not claimed complete**. Gate and Product Knowledge policy status remain under Issue **#406** (Gate 0 PARTIAL as last recorded there). G8 remains a separate Intake gate.

## How to continue

1. Read Issue **#406** for decisions and permissions.
2. Update checklists in this folder only with **observed** path/test evidence (link SHA/run when available).
3. Put Product Knowledge technical traces under **PR #411**, not here.
4. Do not open parallel decision Issues for homepage policy.
