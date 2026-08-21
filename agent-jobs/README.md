# HBI Agent Jobs (Local Runner)

While the PO laptop is online, `hbi-agent-runner.ps1` polls `pending/`, runs **allowlisted** commands only, and writes logs to `results/`.

## Security

- Commands must match a prefix in `allowed.txt`
- Working directory is always the repo root
- No arbitrary shell, no `Invoke-Expression` of free text from chat
- Timeout per job
- Does **not** push secrets; does **not** modify app code

## PO: start once

```powershell
cd E:\hbi
git pull origin master
.\hbi-agent-runner.ps1
```

Leave the window open while working. Ctrl+C to stop.

## AI: submit a job

Add `agent-jobs/pending/job-<id>.json` then commit/push (or ask PO to drop the file).

```json
{
  "id": "job-001",
  "from": "DeepSeek",
  "timeout_sec": 120,
  "command": "python -m pytest",
  "args": ["tests/test_reasoning/", "-v"]
}
```

Read result: `agent-jobs/results/job-<id>.log`
