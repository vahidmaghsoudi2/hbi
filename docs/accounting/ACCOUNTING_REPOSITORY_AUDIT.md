# ACCOUNTING REPOSITORY AUDIT — PHASE 00
**Project:** HBI — vahidmaghsoudi2/hbi  
**Owner (Implementation):** Grok2  
**PO:** Vahid Maghsoudi  
**Baseline SHA:** `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`  
**Audit Date:** 2026-09-01  
**Mode:** READ-ONLY / NO ASSUMPTION / NO IMPLEMENTATION  

---

## 1. CURRENT ARCHITECTURE

Stack observed on master:

| Layer | Reality |
|-------|---------|
| API | FastAPI (`app/main.py`) under `/api/v1/*` |
| DB | SQLite default `sqlite:///./data/hbi.db` (`app/database.py`) |
| ORM | SQLAlchemy models under `app/models/` |
| Schema lifecycle | `Base.metadata.create_all` in `init_db()` — **no Alembic app migrations tree** |
| SQL migration artifact | `scripts/schema_v1.2_migration.sql` (Evidence-focused, not Accounting) |
| Services | `app/services/*` |
| Repositories | `app/repositories/*` |
| Facades/DTOs | `app/interface/facades.py`, `app/interface/dto.py` |
| Frontend | Vite/React `frontend/` — single-page `NewHomePage.tsx` |

Domain flow that already exists (partial):

```
Product (master identity)
   ├─ ProductKnowledge / Evidence → Recommendation
   ├─ Inventory (qty + toman prices)
   └─ Sale / SaleItem (customer sale, toman)
Customer → Case → Recommendation
Customer → Sale
```

There is **no** Accounting subsystem, Accounting Home, or prior `docs/accounting/` content before this audit.

---

## 2. EXISTING PRODUCT SYSTEM

**Master location:** `app/models/product.py` table `Product`

| Field | Present |
|-------|---------|
| `product_id` (PK, string) | YES — single identity key used across HBI |
| `brand`, `product_name` | YES |
| `variant`, `size_value`, `size_unit` | YES |
| `barcode_gtin` (unique, nullable) | YES **on Product**, not on Inventory |
| `identity_status`, `qa_verdict`, `status` | YES (`DRAFT`/`ACTIVE`; identity enum constrained) |
| Category entity / FK | **NO** |
| INCI / actives on Product row | **NO** (knowledge lives in `ProductKnowledge` / Evidence) |

**Services / API:**

- `app/services/product_service.py` — `create_product_with_inventory` creates Product **and** ensures Inventory row
- `app/api/routers/products.py` — GET list/get/by-brand, POST create, PATCH update
- List endpoint returns **verified only** (`identity_status == VERIFIED`)

**Seed / records:**

- `data/seed_products.json` — free-text `category` in JSON **not** a DB Category table
- `docs/01_product_records/PRODUCT_{A,B,C,D}_RECORD.md`

**Integrity rule (Contract §3):** Product Master is centralized. Accounting must **reuse** `Product.product_id`, not invent a parallel catalog.

---

## 3. EXISTING INVENTORY

**Model:** `app/models/inventory.py` table `Inventory`

| Field | Present | Notes |
|-------|---------|--------|
| `inventory_id` | YES | UUID string PK |
| `product_id` FK → Product | YES | |
| `quantity_available` / `reserved` / `damaged` | YES | |
| `stock_status` | YES | sale path may set `OUT_OF_STOCK` |
| `purchase_price_toman` | YES | **Toman**, not USD |
| `sale_price_toman` | YES | **Toman**, not USD |
| Barcode on Inventory | **NO** | barcode is on Product |
| Min stock | **NO** | |
| StockMovement ledger | **NO** | |

**Service:** `app/services/inventory_service.py` — `reserve_stock` / `release_stock` / `confirm_sale`  
**API:** `app/api/routers/inventory.py`

**Product ≠ Inventory:** Partially aligned (separate tables). Gaps: no movement ledger; Toman-only prices.

---

## 4. EXISTING SALES

**Models:** `Sale` (`sale_id`, `customer_id`, `total_amount_toman`, `created_at`); `SaleItem` (qty, `unit_price_toman`, product FK).

**Service:** `app/services/sale_service.py` → `create_sale`:
1. Create Sale total 0
2. Per item: `reserve_stock` → SaleItem → `confirm_sale`
3. Update total

**Negative stock:** `reserve_stock` blocks if insufficient → partial enforcement.  
**Transaction risk:** multi-item loop may partially mutate before failure; needs explicit design + tests.

**API:** `POST /api/v1/sales/` (auth, customer match); `GET /api/v1/sales/total` (global sum semantics).

**Missing:** Payment, discount, USD, FX snapshot, returns, accounting reports.

---

## 5. EXISTING CUSTOMER

`app/models/customer.py` + `app/api/routers/customers.py`.  
`Sale.customer_id` → Customer. Reusable for Accounting counterparty.

---

## 6. EXISTING DATABASE

SQLite; FK ON; `create_all` init; view `CustomerPurchaseHistory`; **no Alembic versions** for Accounting evolution; currency columns are `*_toman` integers.

---

## 7. EXISTING API (Accounting-relevant)

| Prefix | Role |
|--------|------|
| `/api/v1/products` | Product master |
| `/api/v1/inventory` | Inventory read |
| `/api/v1/sales` | Create sale + total |
| `/api/v1/customers` | Sale party |
| `/api/v1/auth` | JWT pilot-token |

**Absent:** stock-in, movements, payments, returns, FX, reports, categories, `/accounting/*`.

---

## 8. EXISTING UI / HOME

`NewHomePage.tsx`: includes a **فروش** panel (toman price, POST sales) — **not** Accounting Home.  
No menu: موجودی / ورود کالا / گردش / گزارش مالی / تنظیمات حسابداری.

---

## 9. EXISTING TESTS

`tests/` covers customer/recommendation/evidence-oriented paths.  
**No dedicated Accounting suite** (StockMovement / FX / Returns / Payment / COGS) evidenced. PHASE 14 required later.

---

## 10. REUSABLE COMPONENTS

| Component | Accounting V1 action |
|-----------|----------------------|
| `Product.product_id` | MUST reuse |
| `Inventory` | EXTEND |
| `Sale` / `SaleItem` | EXTEND carefully |
| `SaleService` + reserve/confirm | EXTEND + ledger |
| `Customer` | REUSE |
| Facades | EXTEND |
| Home nav | EXTEND only in Phase 13 |

---

## 11. ACTUAL GAPS

Accounting Home; Category entity; USD+FX snapshot; StockMovement; Stock In; Payment; Returns; Financial reports; migration discipline; unified availability UX; prior docs/accounting.

---

## 12. CONFLICTS (PO DECISION REQUIRED)

### C-01 Currency of Record
Contract: USD + FX snapshot. Reality: Toman-only columns.  
**Decision:** (A) migrate to USD+FX per contract, or (B) amend V1 to Toman-primary.

### C-02 Category
Contract: Category entity (بوست/مو separate). Reality: free-text in seed only.

### C-03 Barcode
Contract inventory mentions barcode. Reality: `Product.barcode_gtin` only.

### C-04 Sale ledger / partial failure
Direct Inventory mutation without StockMovement vs §9.

### C-05 Protected areas
Do not alter frozen seeds A–D / scoring / evidence for Accounting convenience.

---

## 13. REQUIRED CHANGES (LATER PHASES — NOT NOW)

Architecture map; StockMovement; Stock In; Payment/Return; currency per PO; Category per PO; Accounting Home; Reports; migrations; tests.

---

## 14. NOT REQUIRED (OUT OF SCOPE V1)

Double-entry, payroll, fixed assets, complex tax, multi-branch/warehouse, treasury, full suppliers, FEFO/lot, forecasting, loyalty accounting. No parallel Product Master.

---

## 15. RISK REGISTER

| ID | Risk | Severity |
|----|------|----------|
| R1 | Toman vs USD contract | HIGH |
| R2 | No stock ledger | HIGH |
| R3 | Partial multi-item sale failure | MEDIUM |
| R4 | Global total_sales semantics | LOW-MED |
| R5 | Category free-text drift | MEDIUM |
| R6 | Reco vs stock UX inconsistency | MEDIUM |
| R7 | No Alembic / schema drift | MEDIUM |

---

## 16. RECOMMENDED EXECUTION ORDER

Keep locked phase order. **Before Phase 02 code:** PO resolves C-01 and C-02. Phase 01 must document reuse of Product/Inventory/Sale only.

---

## 17. EVIDENCE PATHS

`app/models/product.py`, `inventory.py`, `sale.py`, `sale_item.py`, `customer.py`  
`app/services/sale_service.py`, `inventory_service.py`, `product_service.py`  
`app/api/routers/sales.py`, `inventory.py`, `products.py`  
`app/main.py`, `app/database.py`  
`frontend/src/pages/NewHomePage.tsx`  
`data/seed_products.json`  
`scripts/schema_v1.2_migration.sql`  
Baseline: `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`

---

## 18. COMMIT SHA

Audit baseline: `8be7a97c3a27c51e05652671e4a33bbe9dc308d0`

---

## 19. PHASE 00 VERDICT

| Criterion | Status |
|-----------|--------|
| Reality mapped | DONE |
| Product Master located | DONE |
| Reuse path Inventory/Sales | DONE |
| Gaps listed | DONE |
| Conflicts for PO | OPEN (C-01, C-02, C-03) |
| Accounting feature implementation | NOT STARTED (correct) |

**PHASE 00 STATUS: COMPLETE (AUDIT ONLY) — AWAITING GATE / PO DECISIONS**

**NEXT PHASE:** NOT STARTED until Gate PASS.

NO ASSUMPTION. NO DUPLICATION. NO SCOPE CREEP. NO NEXT PHASE BEFORE GATE PASS.
