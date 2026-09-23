# HBI Accounting V1 — PO Contract Decisions

## Status
PO DECISIONS RECORDED

## Baseline
Repository: `vahidmaghsoudi2/hbi`
Baseline accounting reality: `docs/accounting/ACCOUNTING_REALITY_BASELINE_v0.2.md`
Baseline commit: `518eee40e87a0fa7bd4847f237ebb2d9e5a92cac`

## V1 Scope

HBI Accounting V1 is intentionally limited to operational commerce and simple financial records:

- Purchases
- Sales
- Purchase and sale amounts
- Inventory
- Payments
- Returns
- Profit / loss
- Purchase and sales history
- Basic operational financial reports

Formal general-ledger accounting is outside V1.

## 1. Money Precision

V1 records monetary amounts as whole **Rial** values.

- No fractional Rial values.
- Final monetary amounts are rounded/represented to the Rial.
- Example: 42,027 Toman is represented as 420,270 Rial.
- The system does not require fractional monetary units in V1.

Any conversion between Toman and Rial must remain explicit and must not introduce fractional Rial values into stored final amounts.

## 2. GL / Double Entry

V1 does **not** implement:

- General Ledger (GL)
- Double-entry bookkeeping
- Debit/Credit journal architecture
- Trial balance
- Formal financial statements

These may be considered in a future scope only through a new PO decision.

## 3. Historical Sales and Document Deletion

Financial history must be preserved.

- A recorded sale must not be physically deleted as the normal correction mechanism.
- If a recorded sale is invalid or needs cancellation, the system should use an explicit business status/action such as VOID/CANCEL rather than erasing the historical record.
- The original record and its audit history remain available.
- Any implementation detail for the exact status/action must be aligned with the existing domain model before coding.

## 4. Financial Audit Ownership

For V1 there is one operational role:

**ADMIN**

The PO is the sole administrator/operator for the current V1 deployment.

There is no separate operator/accountant role in V1.

Financial mutations must therefore be attributable to the authenticated Admin actor using the existing authentication/audit mechanisms where available.

## 5. Concurrency Scope

V1 operational scope assumes:

**one authenticated user at a time.**

The system does not require a production-grade multi-writer concurrency architecture for V1.

Basic transactional integrity and protection against obvious inventory/payment inconsistencies remain required, but stress testing for multiple simultaneous writers is outside V1 acceptance scope.

## 6. Refund Scope

Refund is outside the current V1 Accounting scope unless a later PO decision explicitly adds it.

Returns must preserve the existing return boundary and historical records.

## Acceptance Boundary

Accounting V1 is accepted only when the implementation and tests conform to these decisions and the resulting evidence chain is complete:

`PO Contract → Code → Tests → CI → Runtime Evidence`

This document does not authorize implementation by itself. It records the PO decisions that implementation work must follow.

## Separation

This Accounting V1 contract is independent of PR #204 (ProfileFact consent-negative-path).

PR #206 and subsequent Accounting work must remain separate from ProfileFact work.
