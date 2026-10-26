# Homepage — user path checklist

**Purpose:** Record the real operator path from entering the homepage through product-related operations.  
**Rule:** Mark a step only with evidence (manual observation date, screenshot link, or CI/run URL). Do not mark PASS from code reading alone.

**Authority:** Outcomes that change product policy or Gates must be summarized in Issue **#406** body. Technical ProductKnowledge traces go under **PR #411**.

## Path A — Enter homepage and open product management

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| A1 | Open application home | Homepage loads | NOT RUN | |
| A2 | Locate product management / gallery entry | Entry visible | NOT RUN | |
| A3 | Open product list | List or empty state loads | NOT RUN | |

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

## Path E — QA review surfaces (if reachable from homepage)

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| E1 | Open QA queue/review | Only authorized roles | NOT RUN | |
| E2 | Approve/reject does not silently activate product outside contract | Contract-aligned | NOT RUN | |

## Path F — Encyclopedia → Skin product characteristics

| # | Step | Expected | Result | Evidence |
|---|------|----------|--------|----------|
| F1 | Open «دانشنامه» from homepage | Seven encyclopedia submenus appear | NOT RUN | |
| F2 | Open «ویژگی محصولات پوستی» | Central `docs/homepage/encyclopedia/skin/PRODUCTS.md` opens and shows P1–P7 research dossiers | NOT RUN | |
| F3 | Open «بانک مسائل پوستی» | Specialist P01–P61 registry opens separately | NOT RUN | |
| F4 | Confirm research is not represented as registered/QA-approved products | UI copy preserves the research-only boundary | NOT RUN | |

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
