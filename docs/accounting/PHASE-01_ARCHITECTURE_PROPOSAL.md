# PHASE 01 — ACCOUNTING ARCHITECTURE PROPOSAL
**Project:** HBI — vahidmaghsoudi2/hbi  
**Owner:** Grok2  
**Phase:** 01 — Architecture only (NO code / NO migration execution)  
**PO decisions frozen:** C-01 APPROVED, C-02 APPROVED  
**Mode:** NO ASSUMPTION · NO SCOPE CREEP · NO FROZEN ARTIFACT CHANGE  
**C-01 unit correction:** 2026-09-01 (Conditional Pass remediation)  

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
| `fx_rate_usd_to_irr` | Rate used at posting (**IRR per 1 USD**) |
| `amount_irr` / `amount_toman` | Snapshot display (stored or derived once at post) |

**Invariant:** After commit, historical money rows are immutable w.r.t. FX. Updating “today’s rate” must not cascade-update Sale/SaleItem historical amounts.

### 4.3 Units and conversion (C-01 correction — DESIGN ONLY)

#### 4.3.1 Unit definitions (locked)

| Symbol / field | Unit | Definition |
|----------------|------|------------|
| `purchase_price_toman`, `sale_price_toman`, `unit_price_toman`, `total_amount_toman` | **Toman** | Legacy HBI money columns (integer). Evidence: `app/models/inventory.py`, `sale.py`, `sale_item.py`. |
| **IRR (Rial)** | Iranian Rial | Display/legal denomination alongside Toman. |
| **Toman ↔ IRR** | Fixed ratio | **1 Toman = 10 IRR** (1 IRR = 0.1 Toman). This is **not** an FX rate; it is denomination identity. |
| `R` = `fx_rate_usd_to_irr` | **IRR per 1 USD** | Snapshot/operational FX. Example meaning: R = 1_000_000 means 1 USD = 1_000_000 IRR. |
| `amount_usd` | **USD** | Currency of Record. |

**Forbidden:** `amount_usd = toman / R` when R is IRR-per-USD. That is dimensionally inconsistent (Toman ÷ (IRR/USD)) and causes a systematic **×10 error**.

#### 4.3.2 Canonical conversion chain

```text
Toman  →  IRR  →  USD
```

1. `amount_irr = amount_toman × 10`  
   Units: Toman × (IRR/Toman) → IRR

2. `amount_usd = amount_irr / R`  
   Units: IRR ÷ (IRR/USD) → USD  
   Equivalent: `amount_usd = (amount_toman × 10) / R`

3. New posts after cutover (record USD first):
   - `amount_irr_snapshot = amount_usd × R`
   - `amount_toman_snapshot = amount_irr_snapshot / 10`

#### 4.3.3 Historical migration (design only — not executed in PHASE 01)

For each legacy row with non-null `*_toman`:

1. PO supplies migration-time rate **R** (IRR per 1 USD). PHASE 01 does not invent R.
2. Compute once: `amount_irr = toman × 10`; `amount_usd = amount_irr / R`.
3. Persist `amount_usd`, `fx_rate_usd_to_irr = R`, optional IRR/Toman snapshots for audit.
4. Keep original `*_toman` until dual-read PASS and a later Gate allows drop.
5. Null prices stay null.

**Immutability:** After a historical row is written with its snapshot R, later changes to the operational FX table must **not** rewrite that row’s `amount_usd` or snapshot rate.

#### 4.3.4 Numeric validation example (NOT a PO rate)

Illustrative only — **not** an approved market rate:

| Step | Value |
|------|-------|
| Legacy `purchase_price_toman` | 1_500_000 Toman |
| → IRR | 1_500_000 × 10 = **15_000_000 IRR** |
| Example R | **1_000_000 IRR / USD** |
| → USD | 15_000_000 / 1_000_000 = **15.00 USD** |

Incorrect `toman / R` would yield 1.5 USD and is **rejected**.

#### 4.3.5 Migration strategy principles

1. Additive first (USD + snapshot; retain `*_toman`).
2. One conversion event with PO-supplied R at Phase 04+ execution.
3. No silent invention of prices.
4. Frozen A–D identity content not rewritten for Accounting convenience.
5. Rollback path via retained legacy columns.

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

PHASE 01 architecture includes **unit-correct** C-01 conversion:

`amount_usd = (amount_toman × 10) / R` where R is IRR per 1 USD.

**Request:** `GATE PHASE 01: PASS` after review of §4.3.

Only after PASS may PHASE 02 (Data Model) start.
