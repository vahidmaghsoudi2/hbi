# Skin Problem Bank — Workspace Rules

**Status:** ACTIVE WORKING RULES  
**Scope:** HBI skin-problem knowledge work only.

## 1. Single working location

All working files created for the Skin Problem Bank must live in:

`docs/product-intake-knowledge-registry/`

Do not create workstream files for this unit elsewhere in the repository. Existing historical files outside this folder are read-only source material unless a separately authorized task explicitly says otherwise.

## 2. One source of working truth

Use the workspace index and consolidated reference in this folder as the navigation point when they are available on the working branch. Record substantive findings, source citations, decisions, unresolved questions, and next actions in files in this folder. Do not let PR descriptions, Issue comments, chat summaries, or external notes become a parallel content source.

PRs and Issues remain GitHub workflow mechanisms. When they contain decisions or useful evidence, copy the durable result and its link into the relevant file in this folder.

## 3. File discipline

- Prefer editing the appropriate existing file over creating another file.
- Create a new file only when it has a distinct, necessary purpose; keep it in this folder.
- Keep a clear distinction between evidence, interpretation, proposal, and accepted decision.
- Mark unsupported or unrecovered information `UNKNOWN`; do not reconstruct the accepted Problem Bank list from summaries or structural maps.
- Do not duplicate content across files. Use links between files in this folder when needed.

## 4. Work boundary

This unit covers skin-problem intake and reference knowledge. Product registration/gallery implementation and the future evidence-based problem-to-product relationship layer are separate workstreams. Do not implement product matching, product recommendations, code, database, schema, API, or G8 changes as part of this unit unless explicitly authorized.

## 5. Review and release discipline

Draft candidates are not canonical entries until the required source and human review establish acceptance. Public sources support only the claims they actually make; manufacturer claims are not scientific evidence. Do not use numerical product scores or unsupported confidence values.

Keep PRs unmerged unless explicitly authorized. A successful documentation CI run does not mean the Problem Bank is complete, the original accepted list has been recovered, or G8 is verified.

## 6. Current known blocker

The exact original accepted/refined Problem Bank list has not yet been recovered. Its contents and membership remain `UNKNOWN` until the original artifact is located and verified. Continue bounded evidence preparation for clearly labeled provisional candidates without claiming they are accepted items.
