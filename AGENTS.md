# AGENTS.md

این فایل قواعد و محدودهٔ عملیاتی Agentها (از جمله Copilot و Agentic Workflows) را برای پروژه HBI مشخص می‌کند.

Purpose
-------
Provide a canonical, project-level policy that governs how AI agents may inspect, analyze, propose, and (when allowed) create artifacts in this repository. Preserve human authority for decisions and merges to master.

Principles (must be followed)
-----------------------------
- NO ASSUMPTION: Agents MUST NOT assume facts not present in repository evidence.
- NO INVENTED EVIDENCE: Agents MUST NOT fabricate test results, logs, or evidence.
- NO DIRECT MASTER PUSH: Agents are NOT allowed to push or merge directly to the master (default branch).
- NO UNAUTHORIZED MIGRATION: Agents MUST NOT perform migrations or production-impacting changes without explicit PO approval.
- NO SILENT SCOPE EXPANSION: Agents must not change scope or add components without explicit human agreement.

Allowed agent actions (examples)
---------------------------------
- READ repository files, branches, workflows, and docs.
- ANALYZE code, docs and tests and produce proposals.
- DRAFT PRs and Issues in a feature branch (must include Evidence and "Agent provenance" section in PR body).
- CREATE ISSUE: permitted when agent finds a reproducible problem and attaches raw evidence.
- COMMENT on PR/Issue to summarize findings or point to evidence.
- RUN tests locally or via CI (through PRs) and publish raw artifacts.

Prohibited actions
-------------------
- Direct commit/push/merge to master or protected branches.
- Approve or merge PRs on behalf of humans.
- Invent, redact, or manipulate evidence artifacts.
- Change repository-level settings (branch protection, secrets, permissions) without explicit PO authorization.

Evidence and provenance requirements
------------------------------------
Every agent-generated proposal (Issue, PR, comment, report) MUST include:
1. Agent identifier: name, version, runtime (e.g., Grok vX, Copilot, Agentic-Runner).
2. Exact commands and code used to produce the result (script or API call, including parameters).
3. Exact repository commit SHA used as the input snapshot (git rev-parse HEAD equivalent).
4. Workflow run IDs or timestamps if CI was used as evidence.
5. Attach raw artifacts (pytest-output.txt, coverage.xml, evidence-summary.txt) — do NOT summarize instead of attaching.
6. A short human-readable summary stating limitations and confidence level (e.g., "evidence partial: tests cover 32% of files -- see coverage.xml").

Operational rules for PRs created by an Agent
--------------------------------------------
- Branch naming: agent/<agent-name>/<short-description>/<YYYYMMDDHHMM>
- PR body MUST contain the following sections:
  - Summary
  - What changed (file list)
  - Why
  - Tests executed (exact commands)
  - Evidence artifacts with links (artifact names and workflow run id)
  - Known limitations
  - Agent provenance (as above)
  - Required reviewers and PO decision required (yes/no)
- Tag a human reviewer and the PO in PR description when PO decision is required.

Agent runtime / tokens
----------------------
- Agents MUST use ephemeral tokens scoped to the minimum necessary permissions.
- Long-lived personal access tokens for agents are DISALLOWED unless explicitly approved by PO.
- Agents running inside GitHub Actions should use the built-in GITHUB_TOKEN with minimal write permissions; write permission to master must not be granted.

Safe outputs and automation
---------------------------
- Agentic workflows that run in this repository are allowed to produce reports, issues, comments, and draft PRs.
- Agentic workflows MUST NOT perform merges or write to master.
- Any workflow that needs to write must be explicitly reviewed and approved by PO and limited to a scoped service account.

Enforcement and audits
----------------------
- All agent activity and artifacts MUST be stored or referenced under 07-Evidence/ or in workflow artifacts named with commit SHA.
- Periodic audits of agent activity should be scheduled (e.g., weekly inspector workflow) and reviewed by the PO.

Contact / escalation
--------------------
For any ambiguity or an agent request that requires elevated permission, tag the PO @vahidmaghsoudi2 and create an Issue with label "po-decision-required".

--
This file is a project-level policy. Any modifications to AGENTS.md must be performed via PR and approved by the PO.
