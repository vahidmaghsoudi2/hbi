# HBI Architecture
Last Updated: 1405-05-22 (2026-08-13)

## Backend Layers
| Layer | Path | Gate | Status |
|---|---|---|---|
| Models | app/models/ | 6-1 | APPROVED |
| Repositories | app/repositories/ | 6-2 | APPROVED |
| Services | app/services/ | 6-3 | APPROVED |
| Interface (Facade/DTO/CLI) | app/interface/ | 6-4 | READY FOR REVIEW |

## Data Flow (Decision Support Flow)
Customer -> Case -> Evidence/Knowledge -> Reasoning -> Recommendation -> Product/Inventory -> Outcome

## Architecture Constraints
- Schema v1.1 is LOCKED (change only via Change Request)
- Facades are Use-Case-Oriented, not CRUD-Oriented
- Interface has NO direct access to Repository/Model/Database
