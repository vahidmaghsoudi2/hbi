HBI QA Frameworks v0.1
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

───────────────────────────────────────
[FRAMEWORK 2] QA CHECKLIST v0.1 (Per Product)
───────────────────────────────────────
PHASE 1: IDENTITY (10 checks)
⁃    product_id format valid (BRAND-MODEL-SIZE)
⁃    brand matches manufacturer records
⁃    canonical_name exact (not translated)
⁃    variant specified
⁃    size + unit correct
⁃    barcode_gtin valid (13 digits)
⁃    market_region specified
⁃    packaging_version identified
⁃    inventory_confirmation by PO
⁃    inventory_confirmation_date recorded

PHASE 2: EVIDENCE (8 checks)
⁃    Every claim has a Source
⁃    Source Type classified (OFFICIAL/REGULATORY/RETAILER/SECONDARY)
⁃    Evidence Strength assigned (STRONG/MODERATE/WEAK/UNVERIFIED)
⁃    Claim Type correctly classified
⁃    No INFERENCE registered as FACT
⁃    Source priority: Official > Regulatory > Retailer > Secondary
⁃    Evidence date recorded
⁃    Market region specified

PHASE 3: DATA INTEGRITY (5 checks)
⁃    All Required fields present
⁃    Data types match Schema
⁃    Enum values within allowed set
⁃    No duplicate records
⁃    Foreign keys valid

PHASE 4: BUSINESS RULES (4 checks)
⁃    Price NOT in ProductKnowledge
⁃    Stock NOT in ProductKnowledge
⁃    Dynamic fields marked DYNAMIC
⁃    Purchase History NOT used as Evidence

PHASE 5: FINAL CHECK (5 checks)
⁃    Verdict assigned (VALID/INVALID/CONFLICT/UNKNOWN/NEEDS_REVIEW)
⁃    All PENDING items resolved
⁃    Conflict Register checked
⁃    Unknown Register checked
⁃    PO sign-off recorded

