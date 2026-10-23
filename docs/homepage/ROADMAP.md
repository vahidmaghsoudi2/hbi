# Homepage — operational roadmap

**Type:** Operational execution outline for the HBI homepage UI and related operator flows.  
**Not:** Product Characteristics scientific roadmap (that remains Issue #406).  
**Not:** Implementation authorization.

## Scope

In scope for this operational track (when separately authorized):

- Homepage navigation and product management entry points visible to operators
- Product list / intake / QA review screens as they appear from the homepage
- Product line selection and related UI labels (documentation of behavior only until a code change is authorized elsewhere)
- Linking operator actions to existing backend routes **without** inventing new policy

Out of scope here:

- Skin Problem Space / P01–P61 / PR #433
- ProductKnowledge status semantics implementation (tracked under #406 / #411)
- G8 pilot acceptance (separate ledger)
- Any schema, migration, API, or production data change

## Stages (operational)

| Stage | Intent | Exit criteria (documentation) |
|-------|--------|-------------------------------|
| H0 | Folder and authority map established | This folder exists on an approved PR; links to #406 and #411 are correct |
| H1 | User path inventory | `USER_PATH_CHECKLIST.md` lists the real screens/routes without claiming pass |
| H2 | Evidence slots filled | Each critical path step has PASS/FAIL/NOT RUN + link to SHA or manual note |
| H3 | Gaps filed under correct authority | UI bugs → authorized code path; policy gaps → Issue #406; PK evidence → #411 |

Stages do not auto-authorize implementation. Crossing from documentation to code requires an explicit PO permission recorded in Issue **#406**.

## Dependencies

- Issue #406 for policy/Gates
- Existing product intake and gallery routes already in the application
- PR #411 for Product Knowledge research continuity (when relevant to homepage display of knowledge)

## Acceptance for this documentation PR only

- [x] `docs/homepage/` skeleton created
- [x] No `DECISIONS_AND_STATUS.md`
- [x] No application code changes in the same PR
- [ ] Merged only after PO review of authority map
