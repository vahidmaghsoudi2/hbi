# Home sale Admin-token contract

## Intent
`createSale` on NewHomePage must send `hbi_admin_access_token`, not the pilot/customer `hbi_access_token`.
Buyer remains `customer_id` from the customer session.

## Status
- `frontend/src/api/client.ts` comments updated on this branch (commit history).
- `tests/test_home_sale_admin_token_contract.py` added.
- NewHomePage.tsx must contain:
  - `getAdminAccessToken()` reading `hbi_admin_access_token`
  - `onSaleSubmit` uses `adminToken` for `createSale`
  - Label: customer-scoped total sales

## Do not merge
Until NewHomePage is restored with the above and CI + independent review pass.
