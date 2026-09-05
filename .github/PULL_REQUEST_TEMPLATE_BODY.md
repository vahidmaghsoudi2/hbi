# PR Body (automatically generated)

This PR proposes governance files and templates to establish a safe AI-assisted engineering workflow for HBI.

Changes:
- Add AGENTS.md with strict agent rules and evidence requirements.
- Add PR and Issue templates that require evidence and agent provenance.
- Add CODEOWNERS proposal.
- Add Governance_INDEX and BranchProtection_Checklist in docs/.
- Add inspector report workflow (.github/workflows/inspector-report.yml) and PR summary workflow.

Why:
These files provide the foundational governance to ensure agents cannot modify master or fabricate evidence and to make evidence traceable.

CI & Evidence:
- This PR introduces workflows that run on the branch and generate artifacts (inspector report, pr-summary). Please review artifacts attached to CI runs.

Notes:
- No changes to master or branch protection performed by this PR.
- Apply branch protection per docs/BranchProtection_Checklist.md after review.
