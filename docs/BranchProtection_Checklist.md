# BranchProtection_Checklist.md

Purpose: A step-by-step UI checklist for PO or repo admins to safely apply branch protection to master without disrupting HBI operations.

Pre-flight (read-only)
- [ ] Confirm current default branch is `master`.
- [ ] Create a backup branch: `backup/pre-protection-<YYYYMMDD>` (optional, for historical snapshot).
- [ ] Ensure the working branch `hbi/governance-proposals` is up-to-date and PR is open.

Recommended Branch Protection settings (via Settings → Branches → Add rule)
1. Branch name pattern: `master`
2. Require pull request reviews before merging: ENABLED
   - Require approving reviews: 1 (or 2 for stricter control)
3. Require status checks to pass before merging: ENABLED
   - Add required checks: `test` (job name), `evidence` (if applicable)
   - Require branches to be up to date before merging: ENABLED
4. Include administrators: ENABLED (to avoid admin bypass; PO decision required)
5. Restrict who can push to matching branches: OPTIONAL (leave blank to allow PR workflow)
6. Require linear history: OPTIONAL
7. Prevent force pushes: ENABLED
8. Prevent branch deletion: ENABLED

Actions permissions
- Settings → Actions → General → Workflow permissions
  - Recommended: "Read repository contents and metadata" (disallow write) — then explicitly allow specific workflows if needed.

After applying protection
- [ ] Run a test PR (from `hbi/governance-proposals`) and confirm required checks trigger and PR cannot be merged without reviews and passing checks.
- [ ] Verify artifacts upload and evidence files are produced by CI on the PR.
- [ ] Confirm admin users cannot bypass protections if "Include administrators" was enabled.

PO decisions required
- Approve whether administrators should be able to bypass protections (recommended: NO)
- Identify any trusted CI accounts or GitHub Apps that require push rights and list them explicitly.
- Confirm the required CI job names to add to protection rules.

Rollback plan
- [ ] If a protection rule blocks legitimate automation, remove or adjust the rule and document the change in CHANGELOG_FOR_GOVERNANCE.md.

