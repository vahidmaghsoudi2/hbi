# HBI-RUNTIME-001 — Team 2 Runtime Mission

**Date:** 2026-09-15 (24 Shahrivar 1405)
**Baseline:** `master` @ `f1e3af0c9c864ef41317ff71277abb24946f4b65`
**Status:** IN PROGRESS — PO review/acceptance remains required for any merge to `master`
**Team Manager:** GPT-2

## Mission

Establish a repository-grounded, end-to-end reality trace of the HBI decision runtime and identify integration/quality gaps that materially affect the Decision Runtime. Work must proceed 0→100 within the assigned work packages; discovery of a gap is not, by itself, completion.

## WP-01 — GPT-2

**Owner:** GPT-2
**Scope:** End-to-End Decision Runtime Trace + Integration

Trace the actual runtime path from customer/case context through decision state, need matching, product/evidence/inventory inputs, reasoning, and recommendation output. Verify each handoff against the current repository implementation and contracts. Record concrete evidence, integration breaks, missing links, contradictions, and confidence/limitations. Do not invent states, APIs, roles, data, or behavior.

**Completion target:** a coherent repository-grounded runtime trace with integration findings and evidence sufficient for independent review.

## WP-02 — Grok-2

**Owner:** Grok-2
**Scope:** Product Decision Runtime Reality + API/Quality Surface

Independently audit the product-side decision runtime and its API/quality surface against the same baseline. Verify how product data, evidence readiness/verification, inventory signals, and relevant API/permission/quality boundaries actually participate in decision generation. Identify concrete runtime gaps, inconsistencies, unsafe assumptions, and test/quality weaknesses that can affect recommendation correctness. Cover the assigned surface end-to-end rather than splitting the work into serial micro-tasks.

**Completion target:** a repository-grounded reality report covering the assigned product/runtime/API quality surface, with raw evidence and explicit limitations.

## Team-wide rules

- Reality First: `master` is the Source of Truth for the declared baseline.
- NO ASSUMPTION / NO INVENTED EVIDENCE.
- No direct push or merge to `master`.
- Each owner works 0→100 on the whole assigned work package.
- Findings must distinguish observed facts, gaps, conflicts, and hypotheses.
- Existing reports or memory do not substitute for repository evidence.
- DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED. Independent output verification is mandatory before acceptance.
- Any implementation beyond the audit/report scope requires explicit PO authorization.

## Agent provenance

- Agent identifier: GPT-2
- Runtime: ChatGPT GPT-5.6 Luna, acting as Team 2 manager / WP-01 owner
- Input snapshot: `f1e3af0c9c864ef41317ff71277abb24946f4b65`
- Repository: `vahidmaghsoudi2/hbi`
- Timestamp: 2026-09-15

## First step

Begin WP-01 with a fresh Reality Audit of the current baseline and establish the actual end-to-end runtime trace before proposing any implementation change.
