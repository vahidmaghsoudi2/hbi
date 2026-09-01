# PHASE 01 — ACCOUNTING ARCHITECTURE PROPOSAL
**Project:** HBI — vahidmaghsoudi2/hbi  
**Owner:** Grok2  
**Phase:** 01 — Architecture only (NO code / NO migration execution)  
**PO decisions frozen:** C-01 APPROVED, C-02 APPROVED  
**Mode:** NO ASSUMPTION · NO SCOPE CREEP · NO FROZEN ARTIFACT CHANGE  

---

## 0. Purpose

Define the target Accounting architecture for V1 so that later phases can implement without inventing Product Master, without mixing Product and Inventory, and without rewriting historical money amounts when FX rates change.

This document is **design only**. No schema or application code is modified in PHASE 01.

---

## 1. Frozen PO Decisions

### C-01 — Currency of Record (APPROVED)

| Rule | Statement |
|------|-----------|
| Currency of Record | **USD** |
| Display currencies | USD, IRR, Toman |
| FX Snapshot | Rate at transaction time must be stored with the transaction |
| Historical integrity | Changing the operational FX rate later **must not** rewrite past Sale / Stock-In amounts |
| Current code reality | Inventory/Sale use `*_toman` columns only (see Phase 00 audit) |

### C-02 — Category (APPROVED)

| Rule | Statement |
|------|-----------|
| Category | Independent **data-driven entity** |
| V1 seed set | بوست, مو, زیبایی, ابزار, ادکلن, سایر |
| Independence | **بوست ≠ مو** (no alias, no merge) |
| Product link | Product references one Category; modules must not each keep a private free-text category |

### C-03 — Barcode (from Phase 00; not re-opened)

Barcode remains on **Product** (`barcode_gtin`) as identity. Accounting Inventory does not invent a parallel barcode master.

---

## 2. Target Domain Map (V1)

```
Category (بوست | مو | زیبایی | ابزار | ادکلن | سایر)
   │ 1
   │ N
Product  ← SINGLE Product Master (existing table, product_id)
   ├─ Inventory (qty / prices)
   ├─ SaleItem → Sale → Customer / Payment
   ├─ Recommendation / Case
   └─ ProductKnowledge / Evidence

Inventory qty changes → StockMovement ledger (principle; implement Phase 06)
```

**Hard rules**

- Accounting **does not** create a second Product catalog.
- Product identity ≠ stock availability.
- Recommendation / Consultation consume the **same** `product_id`.
- Sales decrease stock only through controlled inventory operations (+ future StockMovement).

---

## 3. Entity Responsibilities (V1)

| Entity | Owner of truth | Notes |
|--------|----------------|-------|
| Category | New (Phase 02+) | Code + display name; fixed V1 codes |
| Product | Existing master | Identity, brand, name, status, barcode_gtin |
| Inventory | Existing, extend | Qty, stock_status, prices (migrate toward USD fields) |
| StockMovement | New | Trace of IN/OUT/ADJUST/RETURN |
| Sale / SaleItem | Existing, extend | Header + lines; money in USD + snapshot |
| Payment | New | Cash / Card / Transfer / Other |
| Return | Optional V1 if gated | Restock + movement |
| Fx operational rate + snapshot fields | New | Per-transaction snapshot |

Out of scope: double-entry GL, payroll, multi-warehouse, complex tax, FEFO, loyalty.

---

## 4. Currency Architecture

### 4.1 Record vs Display

- **Record:** amounts stored as USD.
- **Display:** UI may show USD, IRR, and Toman using the **transaction snapshot rate** for historical rows, or current operational rate for non-historical screens only.

### 4.2 FX Snapshot (minimum fields)

| Field | Purpose |
|-------|--------|
| `amount_usd` | Currency of record |
| `fx_rate_usd_to_irr` | Rate used at posting (IRR per 1 USD) |
| `amount_irr` / `amount_toman` | Snapshot display (stored or derived once at post) |

**Invariant:** After commit, historical money rows are immutable w.r.t. FX. Updating “today’s rate” must not cascade-update Sale/SaleItem historical amounts.

### 4.3 Migration strategy (Toman → USD) — DESIGN ONLY

**Current evidence:** `Inventory.purchase_price_toman`, `Inventory.sale_price_toman`, `Sale.total_amount_toman`, `SaleItem.unit_price_toman`.

**Principles:**

1. **Additive first:** add USD + snapshot columns/tables; keep legacy `*_toman` until validation PASS.
2. **One conversion event:** migration job uses PO-supplied operational rate **R** at run time (not guessed in PHASE 01):
   - `amount_usd = toman / R` (or equivalent rule locked at Phase 04),
   - store `fx_rate_usd_to_irr = R`,
   - leave original `*_toman` as audit until dual-read PASS.
3. **No silent invention:** null prices stay null.
4. **Frozen A–D:** do not rewrite seed identity content for Accounting convenience.
5. **Rollback:** retain legacy columns until dual-read validated.

PHASE 01 does **not** choose a live FX number, run SQL, or drop toman columns.

---

## 5. Category Design

### 5.1 Target shape

- `category_id` PK (e.g. BOOST, HAIR, BEAUTY, TOOLS, PERFUME, OTHER)
- `name_fa`, optional `name_en`, `is_active`, `sort_order`

V1 fixed independent codes: بوست, مو, زیبایی, ابزار, ادکلن, سایر. **بوست ≠ مو**.

### 5.2 Product link

- FK `category_id` on existing Product (nullability for legacy rows decided in PHASE 02).
- Free-text category in `data/seed_products.json` is not system of record after FK migration.
- Mapping legacy free-text → one of six V1 categories is an explicit PHASE 02/04 data task (not assumed here).

---

## 6. Cross-module integrity (evidence-based)

| Module | Uses Product today | Accounting implication |
|--------|--------------------|-------------------------|
| Product API | `Product.product_id` | Must reuse same id |
| Inventory | FK `product_id` | Stock ≠ identity |
| Sales | `SaleItem.product_id` | No alternate product |
| Recommendation | keyed by `product_id` | Same master |
| Customer/Case | case → recommendation | No parallel catalog |
| Home sales panel | `POST /api/v1/sales/` | Accounting Home extends later |

**File evidence (Phase 00):** `app/models/{product,inventory,sale,sale_item,customer,recommendation}.py`, `app/api/routers/*`.

**Not runtime-verified in this phase:** end-to-end “zero stock ⇒ cannot sell” across Recommendation UI.

---

## 7. Stock movement principle

Quantity changes SHOULD go through StockMovement (STOCK_IN, SALE, RETURN_IN, ADJUSTMENT). Principle only in PHASE 01; implementation in PHASE 06.

---

## 8. Accounting Home (UI boundary)

Presentation-only HBI Home → Accounting Home; menu per contract. No financial logic in browser beyond API calls. Screens in PHASE 03.

---

## 9. Protected / Frozen

Without explicit PO: Frozen Scoring/Evidence, Product A–D record semantics, seed identity content, Recommendation contracts.

---

## 10. Phase boundary

| Allowed PHASE 01 | Forbidden until later gates |
|------------------|-----------------------------|
| This architecture doc | Schema migrations |
| Execution plan update | New `app/models` |
| Recording C-01/C-02 | Accounting UI / Sale code |

---

## 11. Known issues / blockers (later)

1. Toman-only money — needs PO FX rate at migration execution.
2. No StockMovement — sales mutate inventory directly.
3. Seed free-text category mapping not done.
4. Multi-item sale partial failure risk (Phase 00).
5. No dedicated Accounting automated tests yet.

---

## 12. Gate recommendation

PHASE 01 ready for review as architecture freeze of USD+FX rules, Category entity, single Product Master reuse, additive Toman→USD migration design.

**Request:** `GATE PHASE 01: PASS | CONDITIONAL | FAIL`

Only after PASS may PHASE 02 (Data Model) start.
