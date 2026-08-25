# HBI Frontend — Pilot UI

Vite + React + TypeScript. Contracts aligned with backend.

## Pages
- `/` — public product catalog
- `/pilot` — pilot-token auth → create Case
- `/recommendation` — generate & display recommendations

## Run
```bash
cd frontend
npm install
npm run dev
```
Start backend on `http://127.0.0.1:8000`. Vite proxies `/api`.

## Contracts respected
- Case create: `{ customer_id, case_type? }` — no concerns
- TokenPair includes refresh_token
- concerns only in customer_profile on generate
