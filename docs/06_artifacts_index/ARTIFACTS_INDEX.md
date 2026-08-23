# HBI Artifacts Index
Last Updated: 2026-08-23

| Artifact | Path | Notes |
|---|---|---|
| Models | app/models/ | GATE 6-1 approved lineage |
| Repositories | app/repositories/ | Core domain |
| Services | app/services/ | Includes RecommendationService |
| Interface / Facades | app/interface/ | RecommendationFacade path |
| API routers | app/api/routers/ | recommendations + auth pilot path |
| Seed | data/seed_products.json | FROZEN with product records |
| Evidence ledger docs | docs/03_evidence_ledger/ | Record-sourced |
| Pilot QA package | docs/09_gate_reports/HBI_PILOT_READINESS_QA_PACKAGE.md | Current readiness SoT |

## Gaps (honest)
| Item | Status |
|---|---|
| Dedicated EvidenceRepository/Service modules | May still be thin vs full domain ambition — verify code before claiming MISSING absolute |
| Production auth (non pilot-token) | Deferred |
| UI | Deferred |
