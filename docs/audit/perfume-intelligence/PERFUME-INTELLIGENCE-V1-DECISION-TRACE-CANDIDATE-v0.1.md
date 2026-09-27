# Perfume Intelligence V1 — Decision Trace Candidate v0.1

## Status

```text
Status: RESEARCH / TRACEABILITY CANDIDATE
Not an approved Recommendation Contract
```

## Intended future trace

```text
Customer Input → Parsed Intent → Confirmed Preference / Avoidance
→ Current Context → Candidate Products → Product Information / Evidence Used
→ Unknowns → Conflicts → Eligibility Boundary
→ Human-assisted Candidate Explanation → Human Review / Sampling → Observed Outcome
```

## Minimum trace requirements candidate

| Stage | Input | Output | Must not be invented |
|-------|-------|--------|----------------------|
| Customer Input | Customer statement | Source text / structured input | Unstated preference |
| Intent | Customer wording | Extracted or ambiguous intent | Meaning not confirmed |
| Preference | Profile / statement | Like, Avoidance, Deal-breaker | Permanent preference from one event |
| Context | Current request | Occasion / environment where stated | Missing context |
| Product | Identity / availability | Candidate product | Unverified product |
| Evidence | Source records | Attributed information | Unsupported claim |
| Unknown | Missing/unreviewed | Visible unknown | Negative value |
| Conflict | Differing assertions | Visible conflict | Silent averaging |
| Eligibility | Future approved policy | Inclusion / review / stop | Hidden score |
| Explanation | Decision inputs | Human-readable reason | Guaranteed outcome |
| Outcome | Customer report | Contextual event | Universal product truth |

## V1 wording boundary

Allowed: product may be considered because it aligns with stated preference and available information; some information remains unknown and should be reviewed or tested.

Not allowed: definitely the best perfume; exact hours on your skin; medically safe for you.
