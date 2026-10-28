# Product Intake UI scope — Product Owner decision (2026-10-28)

**Status:** Phase 1 UI on branch `ui/intake-catalog-only-po-20261028` (PR #479).
**Anchor:** Issue #406.

## Decisions
- Intake = catalog registration; **smart-complete removed from intake**.
- Unique code = system `HBI-PROD-…` after DuplicateCheck.
- Required business boxes later: name, system code, buy price, sell price, domestic/foreign, product line.
- Phase 1 persists only what API already supports (name, product_line, optional identity fields, DuplicateCheck create).
- Price and domestic/foreign shown as deferred (not sent to API).
- Do not recreate existing seven products.

## Smart-complete in encyclopedia — HOLD
Other teams are defining how intelligent completion should work.
**Do not implement encyclopedia smart-complete until Product Owner provides that design.**
Placement under encyclopedia remains the intended long-term home; implementation is paused.

## Phase 2 (required later)
Persist origin + USD/IRR prices; sale display uses FX without mutating USD purchase price.
