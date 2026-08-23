# Evidence Layer Status

**Owner:** Grok2 (Backend / Integration / Recommendation)  
**HEAD baseline:** `bb3290539866a4e8a8767ab93edc4eee57672deb`  
**Products A–D:** FROZEN — do not modify `docs/01_product_records/*` or `data/seed_products.json`

## Components present in SoT

| Component | Path | Role |
|-----------|------|------|
| Model | `app/models/evidence.py` | Evidence table |
| Repository | `app/repositories/evidence_repository.py` | CRUD |
| Service | `app/services/evidence_service.py` | Business ops |
| Reasoning hard-gate | `app/reasoning/scoring.py` | `evidence_score <= 0` → EVIDENCE_MISSING |
| Identity ledger (project records) | `docs/03_evidence_ledger/ISDIN_PRODUCTS_A_B_C_D_LEDGER.md` | FACT/UNKNOWN from PRODUCT_*_RECORD only |
| Seed (identity claims) | `data/seed_evidence.json` | Loads ledger FACT rows as SECONDARY |
| Index | `docs/07_evidence/EVIDENCE_INDEX.md` | States clinical evidence not registered |

## Controlled EVIDENCE_MISSING

- **Clinical / independent evidence:** still **MISSING** in SoT (no PEER_REVIEWED / REGULATORY rows).
- **Hard-gate:** `MatchScoringEngine` sets `hard_gate_triggered` when `evidence_score <= 0`.
- **Identity ledger FACts** (brand/name/size from product records) use `source_type=SECONDARY` weight 0.2 — they are **not** clinical claims and must not be promoted to FACT clinical without independent sources (Framework 4).
- **Thresholds:** unchanged (no PO decision to alter).

## Tests

- `tests/test_evidence_missing_hard_gate.py` — hard-gate on/off without inventing data.
- `tests/test_vertical_slice_recommendation.py` — Product→seed Evidence→Recommendation (identity-layer only).

## Explicit non-goals (this task)

- No changes to Product A–D records or `data/seed_products.json`
- No invented clinical Evidence
- No Recommendation bypass of scoring engine
- No threshold edits
