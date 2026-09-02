# HBI — PRODUCT INTAKE EXECUTION MISSION

**Mission ID:** PI-GOV-RECON-001  
**Status:** ACTIVE  
**Owner:** Product Intake assigned Owner  
**Authority:** Product Owner + Gate Controller  
**Repository:** `vahidmaghsoudi2/hbi`  
**Branch:** `master`

---

# 1. MISSION

Reconcile all Product Intake governance artifacts with the verified current repository reality.

This is a Governance / Reality / Documentation mission.

It is NOT an implementation mission.

---

# 2. ENTRY GATE

Before any action:

1. Read `docs/01_project_control/PROJECT_RULES.md`.
2. Read Product Intake Strategy.
3. Read Product Intake Reconciliation Amendment.
4. Read Master Execution Roadmap.
5. Read Live Project Ledger.
6. Inspect current `origin/master`.
7. Record actual Current SHA.
8. Perform Reality Audit.

---

# 3. PRIMARY OBJECTIVE

Create one consistent Product Intake command structure so any future Human or AI contributor can determine:

- what HBI Product Intake is;
- what already exists;
- what is missing;
- what is decided;
- what remains OPEN;
- where the project currently is;
- who owns the next action;
- what is forbidden;
- what must happen next.

---

# 4. REALITY-FIRST RULE

Never rely on:

- memory;
- old chat messages;
- old summaries;
- stale SHA;
- assumptions;
- unverified reports.

Repository reality must be directly inspected.

---

# 5. CRITICAL CURRENT REALITY

Existing Product functionality must be treated as baseline.

At minimum inspect:

- `frontend/src/pages/NewHomePage.tsx`
- `frontend/src/pages/ProductIntakePanel.tsx`
- Product API
- Product model
- Product service
- ProductKnowledge
- Evidence
- Inventory
- Product A-D
- Product Master relationships.

---

# 6. NO REBUILD

Do not rebuild:

- Home Page;
- Product Gallery;
- Product Catalog;
- Product Intake;
- Product Master;

when an existing capability already exists.

Use:

CURRENT REALITY
→ GAP ANALYSIS
→ CONTRACT
→ COMPLETION

---

# 7. DATA DOMAIN SEPARATION

Maintain explicit conceptual boundaries between:

- User Input;
- Product Master;
- AI Research Output;
- Evidence;
- Product Knowledge;
- Approval Data.

Do not silently merge these domains.

---

# 8. OPEN DECISIONS

Do not resolve without explicit authority:

- duplicate algorithm;
- duplicate semantics;
- default Product status;
- default Inventory behavior;
- approval endpoint/mechanism;
- approval state machine;
- provisional/shadow behavior;
- Product/Variant architecture;
- history/version schema;
- API Contract details;
- research tier/cost;
- source-tier taxonomy.

---

# 9. IMPLEMENTATION FREEZE

Until Contract v1 is accepted:

**NO:**

- duplicate detection implementation;
- approval endpoint implementation;
- lifecycle implementation;
- Product status policy change;
- Inventory policy change;
- Product Master redesign;
- Product A-D modification.

---

# 10. REQUIRED OUTPUT

The completed mission must leave GitHub with:

1. Reconciliation Amendment;
2. Updated Master Execution Roadmap;
3. Updated Live Project Ledger;
4. This Execution Mission.

Each must be traceable to the reconciliation change.

---

# 11. GIT SAFETY

Never use:

- `git reset --hard`;
- `git clean -fd`;
- force push;
- history rewrite;
- deletion of unrelated files.

Only the four mission files may be staged by this mission.

Existing unrelated Worktree changes must remain untouched.

---

# 12. COMPLETION

This mission is complete only when:

- documents are written;
- files are committed;
- commit is pushed;
- local SHA equals `origin/master`;
- GitHub files are verified;
- Ledger is updated;
- final report is produced;
- handoff is clear.

---

# 13. NEXT UNIT

After this mission:

**PHASE 1 — PRODUCT INTAKE CONTRACT v1**

The next authorized work is Contract definition and formal review.

No implementation precedes Contract acceptance.

# END
