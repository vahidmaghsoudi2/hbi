# HBI Agent Jobs & Write Paths

**Process owner (GitHub Minister):** Grok1  
**Authority:** PO — مهندس مقصودی  
**Workflow doc:** `08-Meeting-Room/HBI_WORKFLOW_V2.md`

---

## What members do

1. Read GitHub (`master`, related files, Actions).
2. Fill **one** package: `TEMPLATES/MEMBER_PACKAGE.txt`.
3. Send package in chat to PO or Grok1.
4. After Write: read Actions + confirm DONE_WHEN yourself.

Do **not** expect multi-step git tutoring. One package only.

---

## What PO does (when AI Write is offline)

1. Open `po-one-paste.ps1`.
2. Set `$GitHubPath`, `$CommitMsg`, `$FileContent` from member package.
3. Run **once**:

```powershell
cd E:\hbi
git pull origin master
# edit po-one-paste.ps1 CONFIG, then:
.\agent-jobs\po-one-paste.ps1
```

Or paste the whole script after filling CONFIG.

4. Open Actions → confirm green on printed SHA.

**Forbidden in PO script path:** token in remote URL; `git -c user.name=SomeAI`.

---

## What Grok1 does (when online)

- Accept member packages / Change Packages.
- Commit to GitHub with provenance in message.
- Trigger or rely on Actions.
- Report TRACE with real SHA.

---

## Local runner (optional)

`hbi-agent-runner.ps1` still polls `pending/` for allowlisted commands while laptop is on.
Primary test evidence path remains **GitHub Actions**.

```powershell
cd E:\hbi
git pull origin master
.\hbi-agent-runner.ps1
```

Job JSON example remains valid under `pending/`.

---

## Folders

| Path | Purpose |
|------|---------|
| `TEMPLATES/` | Member one-package format |
| `pending/` | Optional local runner jobs |
| `results/` | Runner logs |
| `po-one-paste.ps1` | Durable PO write path |
