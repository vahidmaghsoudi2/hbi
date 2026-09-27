# Perfume Intelligence — Evidence, Provenance and Safety Candidate v0.1

## Status

```text
Status: RESEARCH POLICY CANDIDATE
Not an approved HBI Evidence Contract
Not proof of existing Evidence capability
```

## Evidence principle

Evidence must be assessed per attribute. A source is not equally suitable for all claims.

Official Product Page: strong for identity, official name, volume, concentration, official description/notes — not proof of universal longevity, projection or customer preference.

## Candidate source types

Official Product Page; Official Label; Manufacturer Documentation; Regulatory Source; Independent Expert Review; Internal Documented Test; Community Report; Customer Report; Unattributed Source; AI Inference.

## Candidate assertion classes

FACT; MANUFACTURER_CLAIM; OBSERVATION; CUSTOMER_REPORT; INFERENCE; UNKNOWN; CONFLICT.

Conceptual candidates only.

## Rules

```text
Manufacturer Claim ≠ Universal Fact
Customer Report ≠ General Product Fact
AI Inference ≠ Verified Knowledge
Unknown ≠ Negative
Conflict ≠ Low Confidence
```

Confidence and conflict are independent dimensions.

## Safety boundary

Possible future inputs: official warning; documented ingredient information; documented allergen declaration; usage restriction; customer-reported discomfort; sampling consent.

```text
Documented allergen declaration ≠ medical clearance
No disclosed allergen data ≠ no risk
Customer reports discomfort ≠ diagnosed allergy
Customer reports headache ≠ migraine diagnosis
```

When relevant condition is reported during sampling: stop sampling; record report; do not diagnose; follow approved escalation when available.

## External context only (not HBI repository fact)

External reference candidates for later product-specific review:

- IFRA Standards Library: https://ifrafragrance.org/standards-library
- EU Regulation 2023/1545 (fragrance allergen labelling amendments)

These do not replace product label, market/region context or product-specific review.
Label: **external context only** — not architecture decision, not contract requirement, not product-specific fact.
