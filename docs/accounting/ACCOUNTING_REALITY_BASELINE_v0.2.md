# HBI — Accounting Reality Baseline v0.2

**Repository:** vahidmaghsoudi2/hbi  
**Baseline:** `master` @ `2bb1b369982b3133f6976d96a74986dd48db1ff6`  
**Mode:** Independent reality correction  
**Principles:** NO ASSUMPTION / NO INVENTED DATA / Evidence before acceptance

## 1. Purpose

This document supersedes any earlier statement that Accounting V1 is fully accepted when that statement is not supported by the current repository state.

Historical accounting documents remain historical evidence. They are not silently rewritten.

## 2. Current reality classification

| Area | Current classification |
|---|---|
| Sale | PRESENT |
| SaleItem | PRESENT |
| Payment | PRESENT in current inspected code path; control completeness requires verification |
| Inventory | PRESENT |
| StockMovement | PRESENT in current inspected code path; audit completeness requires verification |
| Return | PRESENT |
| Refund | UNVERIFIED |
| Money precision | CONTROL GAP until representation/rounding contract is explicit |
| Sale-total invariant | CONTROL GAP until source-of-truth and invariant are explicit and tested |
| Payment ceiling | CONTROL GAP until explicitly enforced and tested |
| Payment idempotency | CONTROL GAP unless a durable idempotency/reference control is evidenced |
| Sale idempotency | CONTROL GAP unless retry/deduplication behavior is evidenced |
| Inventory concurrency | HIGH RISK until concurrent mutation behavior is tested |
| Inventory auditability | CONTROL GAP if material quantity mutation can bypass StockMovement/audit |
| Financial audit completeness | UNVERIFIED until financial reconstruction fields are evidenced |
| Historical financial integrity | CONTROL GAP/RISK pending delete/cascade and snapshot verification |
| Operational reports | PRESENT where evidenced; not equivalent to General Ledger |
| General Ledger | CONTRACT-DEPENDENT |
| Double Entry | CONTRACT-DEPENDENT |

These classifications do not assert a production financial incident unless a reproducible test or runtime evidence proves one.

## 3. Required accounting invariants

### Sale

For each sale, after applying all Contract-defined adjustments:

`Sale total = sum(SaleItem quantity × unit price) +/− Contract-defined adjustments`

The exact formula must be frozen in the Accounting Contract.

### Payment

Unless the Contract explicitly permits another model:

`sum(valid payments) <= sale total`

Payment lifecycle and what counts as a valid payment must be explicit.

### Inventory

Every material quantity mutation must be reconstructable from the authoritative inventory state and its movement/audit record.

### Return

Returned quantity must respect the Contract-defined refundable/sold quantity.

### Refund

Refunded amount must not exceed the Contract-defined refundable amount.

## 4. Money

Before changing storage types, the Contract must define:

- currency of record
- precision
- rounding mode
- storage representation
- FX source, if FX is in scope
- FX timestamp/snapshot rule

Use of floating-point money is classified as a precision/control risk, not as proof of an accounting error.

## 5. Idempotency

The following retry scenarios require explicit behavior:

- duplicate Sale request
- duplicate Payment request
- concurrent Payment requests
- repeated Return request
- repeated Refund request, if Refund exists

A green happy-path test does not prove idempotency.

## 6. Concurrency

At minimum test:

- stock = 1, two concurrent sales for quantity 1
- concurrent sale and return
- concurrent inventory adjustments
- concurrent payment attempts

The test must inspect final database state, not only HTTP responses.

## 7. Atomicity

Multi-step financial operations must have an explicit transaction boundary.

Failure at any intermediate step must produce a Contract-defined final state.

At minimum test rollback/failure for:

- multi-item Sale
- Sale + Inventory mutation
- Payment
- Return
- Refund, if implemented

## 8. Historical integrity

Changes to current Customer/Profile/Product state must not silently rewrite the meaning of historical financial documents.

Inspect and test:

- delete cascades
- orphan deletion
- foreign-key behavior
- mutable references
- historical snapshots

Financial-document deletion semantics must be Contract-defined: DELETE, VOID, CANCEL, or REVERSE.

## 9. Audit reconstruction

For material financial mutations, evidence should permit reconstruction of:

`WHO / WHAT / WHEN / DOCUMENT / BEFORE / AFTER / WHY / REQUEST-CORRELATION / RESULT`

Generic mutation logging is not automatically equivalent to complete financial auditability.

## 10. Accounting scope

Do not infer General Ledger or Double Entry from operational sales/payment/reporting features.

If V1 scope does not require formal accounting:

- General Ledger = CONTRACT-DEPENDENT
- Double Entry = CONTRACT-DEPENDENT

Operational reports must not be represented as a General Ledger.

## 11. Acceptance rule

Accounting End-to-End is not accepted merely because CI is green.

Acceptance requires:

`Contract → Implementation → Negative Tests → Integration Tests → Concurrency Tests → CI → Runtime Evidence → Audit Evidence`

Any missing link remains OPEN/UNVERIFIED.

## 12. Work split

### This branch: documentation/reality baseline only

This branch establishes the corrected baseline and control requirements. It does not silently implement financial behavior.

### Grok implementation phase

Grok owns:

1. inspect current code against this baseline
2. identify exact implementation gaps
3. create/update the Accounting Contract where a PO decision is required
4. implement only approved controls
5. add negative/integration/concurrency/idempotency/rollback tests
6. run full CI
7. execute runtime evidence
8. open a dedicated implementation PR
9. perform post-merge verification

## 13. Separation from PR #204

PR #204 is the ProfileFact consent-negative-path change.

Accounting implementation must not be mixed into PR #204.

## 14. Final status

**ACCOUNTING END-TO-END RELIANCE: BLOCKED PENDING EVIDENCE**

This is a control/acceptance status, not a claim that HBI has suffered a financial loss or production accounting incident.
