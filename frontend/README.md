# HBI Frontend — Contract Foundation

Aligned with backend API contracts (no invented endpoints or fields).

## Corrected contracts (vs earlier package drafts)

| Item | Correct shape |
|------|----------------|
| Case create | `{ customer_id, case_type? }` — **no `concerns`** |
| TokenPair | `{ access_token, refresh_token, token_type }` |
| RecommendationDTO | includes optional AD-3 fields (`final_score`, `confidence`, `eligibility`, `reasoning`, `availability`, `price`, …) |
| Concerns | only inside `RecommendationRequest.customer_profile` |

## Base URL

Set `VITE_API_BASE` (default `/api/v1`).

## Auth

- `POST /auth/pilot-token` — development/pilot only
- All Case / Recommendation calls require `Authorization: Bearer <access_token>`
- Products listing is public

## Next

UI pages (home, case, recommendation) can be built on top of `src/api/client.ts` and `src/types/api.ts` without further contract changes.
