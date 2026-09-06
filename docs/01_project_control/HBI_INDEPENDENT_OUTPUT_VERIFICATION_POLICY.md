# HBI — Independent Output Verification & Trust Control Policy

**Policy ID:** HBI-GOV-IOV-001  
**Version:** V1.0  
**Status:** REGISTERED & ACTIVE (Merged to master)  
**Authority:** Product Owner — Vahid Maghsoudi  
**Repository:** vahidmaghsoudi2/hbi  
**Merge Commit SHA:** `adbd45025a36e8b054853e160f986392f24e3aae`  
**Branch of introduction:** `governance/independent-output-verification-policy`  
**Baseline master SHA at drafting:** `231310cfef4cab128450eabc61ebf66cbfe32092`  
**Effective:** 2026-09-06 (Merged in `adbd450` with PO acceptance)

---

## 1. Purpose

This policy creates a formal, non-personal control layer for **independent validation of Work Owner claims**.

It exists so that correctness of a deliverable is never accepted solely because the Agent or team member who produced it reports it as correct.

This policy addresses a specific gap: **Independent Verification of Work-Product Claims**.

It does **not** replace, rewrite, or weaken existing rules in:

- `docs/01_project_control/PROJECT_RULES.md` (NO ASSUMPTION, NO INVENTED DATA, Reality Audit, Evidence, ONE TASK = ONE OWNER, Definition of Done, Frozen/Accepted, PO Authority, etc.)
- `docs/01_project_state/MISSION_OWNERSHIP_POLICY.md`
- `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md`
- Safe Git / PR / no direct master push practices already in force

Where this policy and an existing rule both apply, both apply. This policy adds the **independent** check; it does not restate the Owner’s self-check duties.

---

## 2. Foundational Principle

> **No Agent Output Is Trusted Solely Because the Agent Reports It as Correct.**

Operational meaning:

No output is considered **Verified** merely because its producer reported success. Correctness must be supported by **reproducible Evidence** and, where required by risk, by **Independent Verification**.

This applies equally to every Agent and human contributor (ChatGPT, Grok, Qwen, Copilot, DeepSeek, or any other). **No Agent is exempt.**

This policy is **not** a statement of distrust toward team members. It transfers trust from individual report to an **auditable process**.

---

## 3. Status Separation (Mandatory Vocabulary)

The following are distinct and must not be conflated:

| Status | Meaning |
|--------|--------|
| **DONE** | Work Owner asserts Scope complete, changes delivered, self-checks and Evidence produced. |
| **VERIFIED** | An Independent Verifier (or PO acting as Verifier) has confirmed claims against Repository Reality and Evidence. |
| **ACCEPTED** | Product Owner formally accepts the work for the project (may include residual limitations). |
| **MERGED** | Change is integrated into `origin/master` after required approvals. |

```
DONE ≠ VERIFIED
VERIFIED ≠ ACCEPTED
VERIFIED ≠ MERGED
```

Standard lifecycle (logical order; execution of Work Packages may still run in parallel):

```
ASSIGNED
   → EXECUTED
   → SELF-CHECKED
   → EVIDENCE
   → INDEPENDENTLY VERIFIED
   → PR REVIEW
   → PO ACCEPTANCE
   → MERGE
```

**Parallel execution does not mean parallel acceptance.**  
Work Packages may execute concurrently; acceptance and merge remain gated by verification and PO decision as required by risk.

---

## 4. Roles

### 4.1 Work Owner

Responsible for end-to-end delivery of the assigned Work Package (consistent with existing ONE TASK = ONE OWNER rule):

- Execute Scope
- Produce changes
- Run required tests
- Produce Evidence
- State Limitations explicitly
- Deliver reproducible outputs (branch, commit, paths, commands, results)

The Owner’s self-report is **necessary but not sufficient** for Verification of high-risk work.

### 4.2 Independent Verifier

A party **other than the Work Owner** (another Agent, human, or PO) who:

- Inspects Repository Reality (tree, diff, commit SHA)
- Checks Acceptance Criteria coverage
- Reviews tests and Evidence
- Re-runs tests when risk or doubt warrants
- Exercises negative / rejection paths for sensitive packages when applicable
- Issues an independent **Verdict** (see §5)

The Verifier must **not** merely rubber-stamp the Owner’s report. If the Owner’s claim and Repository Reality diverge, Repository Reality wins (see §7).

PO may act as Verifier. The same Agent must not be both sole Owner and sole Verifier for High-Risk work unless PO explicitly records an exception.

---

## 5. Verification Verdicts

| Verdict | Definition |
|---------|------------|
| **VERIFIED** | Claims match Repository Reality; Acceptance Criteria covered; Evidence sufficient and reproducible; no material Limitations left open for the stated Scope. |
| **VERIFIED WITH LIMITATIONS** | Core claims hold; known Limitations are documented, scoped, and acceptable for interim progress; not treated as full Complete for high-risk gates. |
| **PARTIAL** | Some Acceptance Criteria or Evidence hold; material gaps remain; must not be reported as Complete. |
| **FAILED** | Material claim fails against Reality, tests, or Criteria. |
| **UNVERIFIABLE** | Insufficient access, missing Evidence, or environment prevents independent confirmation; treated as not Verified until resolved. |

These verdicts are independent of the Owner’s “DONE” claim and of PO “ACCEPTED” / merge decisions.

---

## 6. Risk-Based Verification

Verification effort must be proportional to failure impact.

| Risk tier | Guidance |
|-----------|----------|
| **Low** | Light verification (diff + key claims + Evidence presence). |
| **Medium** | Full verification of Scope, tests, and Evidence; selective re-run of tests. |
| **High** | Independent Verification **required**. Self-check alone is insufficient. |

**High-risk domains (non-exhaustive):**

- Database / Migration
- Accounting
- Inventory / Stock
- Authentication / Authorization
- Product Lifecycle / Governance fields
- Evidence / QA readiness
- Recommendation logic
- API Contracts
- Financial logic
- Audit Trail / Mutation Log

PO may elevate any package to High Risk.

---

## 7. Repository Reality Is Authoritative

When Agent report and Repository Reality conflict:

**Repository + reproducible Evidence prevail.**

Examples:

- Claimed test “added” but absent from Diff → test was **not** added.
- Claimed “tests passed” without runnable Evidence → Pass is **not** valid.
- Claimed “WP complete” with unmet Acceptance Criteria → WP is **not** Complete.

This reinforces existing SOURCE OF TRUTH and Evidence rules; it does not replace them.

---

## 8. False Completion (Prohibited)

The following are not acceptable:

- Claiming tests were run without actual execution
- Claiming Pass without Evidence
- Claiming files/code changes that do not exist in the Repository
- Presenting assumptions as facts
- Hiding material Limitations
- Presenting Partial work as Complete

When uncertain, the required labels remain those already defined in PROJECT_RULES (e.g. UNKNOWN, NOT VERIFIED, CONFLICT). Under this policy, unresolved uncertainty maps to **UNVERIFIABLE** or **PARTIAL**, never silent Complete.

---

## 9. Error → Prevention

Material errors found during Independent Verification should, when appropriate, follow:

```
ERROR
  → ROOT CAUSE
  → FIX
  → REGRESSION TEST (when code/behavior is involved)
  → GOVERNANCE / PROCESS IMPROVEMENT (when process gap is involved)
```

Goal: a discovered error should incur cost once, not repeatedly.

---

## 10. Operational Trust Classification

Operational Trust is an **Evidence-based**, PO-controlled classification of reliability of past outputs. It is **not** a personal or emotional ranking of Agents.

Inputs (examples):

- Ratio of Verified outputs
- Evidence quality
- Test reliability
- Scope compliance
- Accuracy vs Repository Reality
- Quality of Self-Critique / Limitations disclosure
- Count and severity of verification failures
- Repeated errors
- Claims without Evidence

Suggested levels (PO assigns/revises):

| Level | Operational meaning |
|-------|---------------------|
| **TRUSTED** | Consistent Verified history; lower verification intensity may be appropriate for Low/Medium risk. |
| **CONDITIONAL** | Acceptable with normal Independent Verification. |
| **RESTRICTED** | Elevated verification; High-Risk packages may require explicit PO oversight. |
| **REMOVED** | Not assigned new ownership until PO restores status. |

Classification is reviewable and remains under PO authority. Absence of a formal score does not suspend this policy’s verification requirements.

---

## 11. Relation to Existing Governance

| Topic | Primary existing source | This policy adds |
|-------|-------------------------|------------------|
| No assumption / no invented data | PROJECT_RULES §2–3 | — (does not restate) |
| Reality Audit / Source of Truth | PROJECT_RULES §1, §5 | Independent check that claims match Reality |
| Evidence | PROJECT_RULES §16 | Evidence must support Independent Verdict |
| One Owner end-to-end | PROJECT_RULES §10, §24; MISSION_OWNERSHIP_POLICY | Separates Owner from Independent Verifier |
| Definition of Done | PROJECT_RULES §32 | Done is Owner-side; Verified is Verifier-side |
| Frozen / Accepted / PO | PROJECT_RULES §23, §25 | Acceptance remains PO; Verification is prerequisite for high risk |
| No direct master / PR | Safe Git practices | Unchanged |

---

## 12. Registration

- Canonical file: `docs/01_project_control/HBI_INDEPENDENT_OUTPUT_VERIFICATION_POLICY.md`
- Indexed from: `docs/Governance_INDEX.md`
- Change type: **Governance-only** (no production application code)
- Merge: only after explicit PO approval

---

## 13. Change Control

Amendments require:

1. Explicit PO decision
2. Version bump
3. Repository update via PR
4. Impact note on dependent processes

---

**End of Policy V1.0**
