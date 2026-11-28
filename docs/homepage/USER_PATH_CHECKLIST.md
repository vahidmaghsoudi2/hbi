# Homepage — user path checklist

**Purpose:** Record the real operator path from entering the homepage through product-related operations.  
**Target IA:** [Product-management target](./product-management/README.md) and [PO decision #406](https://github.com/vahidmaghsoudi2/hbi/issues/406) supersede older navigation labels below where they conflict. This checklist records expected paths; it does not claim runtime implementation.
**Rule:** Mark a step only with evidence (manual observation date, screenshot link, or CI/run URL). Do not mark PASS from code reading alone.

**Authority:** Outcomes that change product policy or Gates must be summarized in Issue **#406** body. Technical ProductKnowledge traces go under **PR #411**.

## Path A — Enter homepage and open product management

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| A1 | Open application home | Homepage loads | NOT RUN | |
| A2 | Locate product management / gallery entry | Entry visible | NOT RUN | |
| A3 | Open «فهرست کالاها» as the product-management entry point | List or empty state loads | NOT RUN | |
| A4 | Create/open a product from the list | One product dossier opens | NOT RUN | |
| A5 | Edit product identity, attributes and evidence | Changes remain in the same product dossier | NOT RUN | |

## Path B — Product line and intake entry

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| B1 | Open create/edit product flow | Form available when authorized | NOT RUN | |
| B2 | See product line options | SKIN / HAIR / BEAUTY / TOOLS / OTHER (label per current UI) | NOT RUN | |
| B3 | Validation when line missing | Error shown; submit blocked | NOT RUN | |

## Path C — Identification / GTIN (if exposed on homepage flows)

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| C1 | Lookup existing GTIN | Unique match routes to existing product (read-only behavior per authorized WP) | NOT RUN | |
| C2 | Unknown GTIN | Routes to formal intake; no silent create | NOT RUN | |
| C3 | Ambiguous match | Ambiguity handled without inventing identity | NOT RUN | |

## Path D — Evidence / knowledge surfaces (if reachable from homepage)

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| D1 | View product knowledge | Displays stored fields; does not invent values | NOT RUN | |
| D2 | Refresh knowledge (if UI exposes it) | Behavior matches authorized API; status semantics per #406/#411 | NOT RUN | |

## Path E — Embedded quality controls before PO decision

There is no standalone QA destination in the target navigation. The controls remain within product preparation and must be evidenced before final PO approval.

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| E1 | Verify product identity, version/market and duplicate checks | Result visible in the product dossier | NOT RUN | |
| E2 | Review Evidence provenance/readiness, completeness, conflicts/UNKNOWN and applicable skin-safety checks | Findings and reviewer result traceable before PO decision | NOT RUN | |
| E3 | PO approval | Accepted product transitions directly to ACTIVE; no separate post-PO activation | NOT RUN | |

## Path F — Product management → product dossier / skin problems

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| F1 | Open «مدیریت محصولات» then «فهرست کالاها» | Product list is the entry point | NOT RUN | |
| F2 | Open a product dossier | Product characteristics and evidence are in the same dossier | NOT RUN | |
| F3 | Open «مشکلات پوستی» | Specialist P01–P61 registry remains the canonical problem source | NOT RUN | |
| F4 | Confirm six non-skin knowledge domains remain accessible | Existing access paths are preserved until separately decided | NOT RUN | |
| F5 | Confirm P1–P7 research is not represented as registered/accepted Product Master records | UI copy preserves the research-only boundary | NOT RUN | |

## Legend

| Result | Meaning |
|--------|--------|
| NOT RUN | Not yet executed in this checklist |
| PASS | Observed with evidence link |
| FAIL | Observed failure with evidence link |
| BLOCKED | Cannot run; reason in Evidence column |

## Notes

- Empty evidence columns are intentional at skeleton time.
- Filling this checklist is documentation work; fixing FAIL items may require a separate authorized code change and must not be implied by editing this file alone.
