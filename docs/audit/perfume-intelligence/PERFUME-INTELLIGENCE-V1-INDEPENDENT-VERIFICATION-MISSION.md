# Perfume Intelligence V1 — Independent Verification Mission

## Status

```text
Status: READY FOR EXECUTION WHEN VERIFIER AVAILABLE
Currently: BLOCKED — REPOSITORY ACCESS NOT AVAILABLE
Architecture: NOT DECIDED
Contract: NOT AUTHORIZED
Implementation: NOT AUTHORIZED
```

## Purpose

Answer only: Has the Audit Author reported current HBI reality accurately, with evidence, without exaggeration?

Not architecture. Not contract. Not implementation.

## Source artifacts

```text
Repository: vahidmaghsoudi2/hbi
Audit branch: docs/perfume-v1-reality-integration-audit
Audit file: docs/audit/PERFUME-INTELLIGENCE-V1-HBI-REALITY-INTEGRATION-AUDIT.md
Code baseline SHA: bbe1a4eed81937fae1c7ecb7be5bb28af551458b
```

## Mandatory amendments

1. **Append-only** — do not rewrite Audit Author text; append Independent Verification + visible disagreement.
2. **Claim Classification** — REPOSITORY_FACT | TEST_SUPPORTED_FACT | CI_SUPPORTED_FACT | RUNTIME_FACT | INFERENCE | ASSUMPTION | UNKNOWN | CONTRADICTED.
3. **CI status** — Missing CI ≠ Failed CI. Use CI_PASSED | CI_FAILED | CI_NOT_AVAILABLE | CI_NOT_PRESERVED | CI_NOT_VERIFIED | CI_NOT_REQUIRED.
4. **Runtime** — only where applicable; else NOT_REQUIRED or NOT_AVAILABLE.
5. **Documentation ≠ Repository Behavior.**

## Verifier eligibility

Must not be Grok (Audit Author). Must have real repository access. Must inspect Base SHA and evidence package.

## Completion fields

1. New Commit SHA (if append)  
2. Independent Verification Verdict  
3. Per-row results PI-V1-01 … PI-V1-10  
4. Rows NEEDS_MORE_EVIDENCE / NOT_CONFIRMED / CANNOT_VERIFY  
5. Visible disagreement with Grok  
