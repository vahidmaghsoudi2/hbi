# Product Intake UI scope — Product Owner decision (2026-10-28)

**Status:** Phase 1 UI in progress on branch `ui/intake-catalog-only-po-20261028`.
**Anchor:** Issue #406.

## Decisions
- Intake = catalog registration; smart-complete removed from intake.
- Smart-complete lives under encyclopedia (skin first; other lines follow same pattern).
- Unique code = system `HBI-PROD-…` after DuplicateCheck.
- Required business boxes later: name, system code, buy price, sell price, domestic/foreign, product line.
- Phase 1 persists only what API already supports (name, product_line, optional identity fields, DuplicateCheck create).
- Price and domestic/foreign shown as deferred (not sent to API).
- Do not recreate existing seven products.

## Phase 2 (required later)
Persist origin + USD/IRR prices; sale display uses FX without mutating USD purchase price.
