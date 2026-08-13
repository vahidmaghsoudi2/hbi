from pathlib import Path

PROJECT = Path("E:/HBI")

print("=" * 60)
print("Creating Reference Documents")
print("=" * 60)

# frameworks.txt
frameworks_path = PROJECT / "docs" / "04_frameworks" / "frameworks.txt"
frameworks_path.parent.mkdir(parents=True, exist_ok=True)

frameworks_content = """HBI QA Frameworks v0.1
Last Updated: 1405-05-20

This document defines the Quality Assurance frameworks for the HBI project.

═══════════════════════════════════════════════════════════
FRAMEWORK 1 — Product Identity Validation Contract
═══════════════════════════════════════════════════════════

Purpose:
Validate product identity based on 10 canonical fields before any
knowledge or evidence is attached.

Required Fields (all must be present and verified):
1. Brand (canonical name)
2. Product Name (canonical name)
3. Variant (SPF, Anti-aging, etc.)
4. Size Value (numeric)
5. Size Unit (ml, g, etc.)
6. Barcode / GTIN
7. Market Region (EU, Iran, etc.)
8. Country of Origin
9. Packaging Version
10. Inventory Confirmation (physical verification)

Identity Status Levels:
- IDENTIFIED: All 10 fields verified with high confidence
- PARTIALLY_IDENTIFIED: 7-9 fields verified
- UNIDENTIFIED: Less than 7 fields verified

Validation Rules:
- No knowledge or evidence can be attached to UNIDENTIFIED products
- PARTIALLY_IDENTIFIED products can have limited knowledge
- Only IDENTIFIED products can have full Evidence Ledger

Framework 1.A — Validation Contract
The validation contract requires all 10 fields to be present and verified
before a product can move to the Evidence Gathering phase.

Framework 1.D — Separation of Concerns
Price and stock information must NEVER appear in ProductKnowledge.
They belong exclusively in the Inventory layer.

═══════════════════════════════════════════════════════════
FRAMEWORK 3 — Evidence Ledger
═══════════════════════════════════════════════════════════

Purpose:
Maintain a structured ledger of all evidence supporting product claims.

Required Fields for Each Evidence Entry:
1. claim_id (format: EV-PRODUCTID-NNN)
2. claim_text (the actual claim)
3. field (which product field this evidence supports)
4. claim_type (FACT / MANUFACTURER_CLAIM / EVIDENCE_SUPPORTED / INFERENCE / UNKNOWN)
5. source (URL or reference)
6. source_type (OFFICIAL_MANUFACTURER / REGULATORY / REPUTABLE_RETAILER / SECONDARY)
7. source_date (ISO 8601)
8. evidence_date (when evidence was gathered, ISO 8601)
9. evidence_strength (STRONG / MODERATE / WEAK / UNVERIFIED)
10. market_region (which market this applies to)
11. notes (optional)
12. qa_status (PENDING / VERIFIED / REJECTED / NEEDS_REVIEW)

Source Priority (for conflict resolution):
1. OFFICIAL_MANUFACTURER (highest)
2. REGULATORY
3. REPUTABLE_RETAILER
4. SECONDARY (lowest)

Evidence Strength Levels:
- STRONG: Multiple high-quality sources, consistent
- MODERATE: Single high-quality source or multiple moderate sources
- WEAK: Single moderate source or multiple weak sources
- UNVERIFIED: Cannot be verified

═══════════════════════════════════════════════════════════
FRAMEWORK 4 — Claim Boundary Rules
═══════════════════════════════════════════════════════════

Purpose:
Prevent unauthorized promotion of claim types.

Promotion Rules:
- UNKNOWN cannot be promoted to anything
- INFERENCE cannot be automatically promoted to FACT
- MANUFACTURER_CLAIM cannot be promoted to FACT without independent evidence
- EVIDENCE_SUPPORTED can be promoted to FACT only with multiple STRONG sources
- FACT is the highest level and cannot be promoted further

Claim Types (in order of reliability):
1. FACT (highest) - Independently verified with strong evidence
2. EVIDENCE_SUPPORTED - Supported by evidence but not independently verified
3. MANUFACTURER_CLAIM - Claimed by manufacturer, not independently verified
4. INFERENCE - Inferred from other data, not directly stated
5. UNKNOWN (lowest) - No information available

═══════════════════════════════════════════════════════════
FRAMEWORK 5 — Unknown/Conflict Protocol
═══════════════════════════════════════════════════════════

Purpose:
Handle missing or conflicting data without silent failure.

Unknown Handling:
- Critical fields: Product verdict = NEEDS_REVIEW, action = ESCALATE_PO
- Non-critical fields: Product verdict = VALID, action = LOG_UNKNOWN_REGISTER
- Never guess or fill in missing data

Conflict Handling:
- Unresolvable conflicts: Status = CONFLICT_UNRESOLVED, action = ESCALATE_PO
- Resolvable by priority: Select highest-priority source, log resolution
- Resolvable but unknown priority: Status = NEEDS_REVIEW, action = ESCALATE
- Never silently pick a value without logging

Conflict Register:
All conflicts must be logged in a Conflict Register with:
- Product ID
- Field name
- Conflicting values
- Sources
- Resolution status
- Resolution action

Unknown Register:
All unknown fields must be logged in an Unknown Register with:
- Product ID
- Field name
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Action taken

═══════════════════════════════════════════════════════════
END OF FRAMEWORKS
═══════════════════════════════════════════════════════════
"""

if not frameworks_path.exists():
    frameworks_path.write_text(frameworks_content, encoding="utf-8")
    print("[FILE] created: docs/04_frameworks/frameworks.txt")
else:
    print("[SKIP] already exists: docs/04_frameworks/frameworks.txt")

# HBI_Handover.txt
handover_path = PROJECT / "docs" / "01_project_state" / "HBI_Handover.txt"
handover_path.parent.mkdir(parents=True, exist_ok=True)

handover_content = """HBI Project Handover Document
Date: 1405-05-20 (2026-08-11)
From: Qwen — Knowledge Engineer / Data QA
To: Maqsoudi Gallery Team

═══════════════════════════════════════════════════════════
PROJECT OVERVIEW
═══════════════════════════════════════════════════════════

Project: HBI (Health & Beauty Intelligence)
Owner: Vahid Maghsoudi (Product Owner)
Phase: Phase 1 — Vertical Slice (Products A and B from ISDIN)

Architecture Layers:
1. Models (GATE 6-1)
2. Repositories (GATE 6-2)
3. Services (GATE 6-3)
4. Interface (GATE 6-4)

═══════════════════════════════════════════════════════════
GATE STATUS
═══════════════════════════════════════════════════════════

GATE 5 — Schema Lock v1.1
Status: LOCKED & APPROVED
Notes: Schema is locked. Changes only via formal Change Request.
Finding: Table name "Case" requires quoting in raw SQL due to reserved keyword.

GATE 6-1 — Models
Status: NOT APPROVED (as of 1405-05-20)
Notes: DeepSeek was fixing issues. May have been approved since then.
Models: Product, ProductKnowledge, Evidence, Customer, Case,
        Recommendation, Inventory, Sale, SaleItem (9 total)

GATE 6-2 — Repository Layer
Status: Not explicitly documented in this handover
Notes: BaseRepository + 7 domain repositories exist.
Missing: EvidenceRepository, ProductKnowledgeRepository

GATE 6-3 — Service Layer
Status: Not explicitly documented in this handover
Notes: BaseService + 6 domain services exist.
Missing: EvidenceService, ProductKnowledgeService

GATE 6-4 — Interface Layer
Status: Not started as of 1405-05-20
Notes: Contract reconciliation (6-4A) was in progress.

═══════════════════════════════════════════════════════════
KNOWN GAPS (as of 1405-05-20)
═══════════════════════════════════════════════════════════

1. EvidenceRepository — MISSING
2. EvidenceService — MISSING
3. ProductKnowledgeRepository — MISSING
4. ProductKnowledgeService — MISSING
5. Reasoning Engine — SKELETON ONLY
   (RecommendationService._calculate_match_score returns fixed 0.75)
6. Consent management (update_consent, withdraw_consent) — MISSING

═══════════════════════════════════════════════════════════
PRODUCTS STATUS
═══════════════════════════════════════════════════════════

Products A and B (ISDIN):
- Identity Status: VERIFIED
- Evidence: Awaiting collection
- Gate: Ready for Evidence Gathering

Products C and D:
- Identity Status: UNIDENTIFIED
- Issue: Awaiting physical information from Product Owner
- Gate: Blocked until identity is established

═══════════════════════════════════════════════════════════
DECISIONS MADE
═══════════════════════════════════════════════════════════

ADR-001: Use quoted table name "Case" in raw SQL
Status: ACCEPTED
Date: 1405-05-21
Reason: "Case" is a reserved keyword in SQLite. ORM handles quoting
        automatically, but raw SQL must use "Case" with quotes.

ADR-002: Do not implement Evidence/ProductKnowledge in GATE 6-4B
Status: ACCEPTED
Date: 1405-05-21
Reason: These services do not exist in GATE 6-3. Interface layer
        should only expose capabilities that have real backend support.

═══════════════════════════════════════════════════════════
NEXT STEPS (as of 1405-05-20)
═══════════════════════════════════════════════════════════

1. Complete GATE 6-4B (Interface Implementation)
2. Perform Reality Check to confirm what is actually built
3. Build the real Reasoning Engine (replace skeleton)
4. Implement EvidenceRepository and EvidenceService
5. Implement ProductKnowledgeRepository and ProductKnowledgeService
6. Gather evidence for Products A and B (ISDIN)
7. Establish identity for Products C and D

═══════════════════════════════════════════════════════════
END OF HANDOVER
═══════════════════════════════════════════════════════════
"""

if not handover_path.exists():
    handover_path.write_text(handover_content, encoding="utf-8")
    print("[FILE] created: docs/01_project_state/HBI_Handover.txt")
else:
    print("[SKIP] already exists: docs/01_project_state/HBI_Handover.txt")

print("=" * 60)
print("DONE. Reference documents created.")
print("=" * 60)