"""
HBI Phase 2 — GATE 6-3: Pydantic V2 Schemas for Recommendation API
====================================================================
Source of Truth:
  - app/interface/dto.py (RecommendationDTO — 16 AD-3 fields)
  - app/models/recommendation.py (SQLAlchemy Recommendation model)

Constraints:
  - Schema v1.1 is LOCKED. No DB changes.
  - Framework 1.D: price/availability are DYNAMIC (from Inventory, NOT in ProductKnowledge).
  - Framework 5: UNKNOWN/CONFLICT handling preserved.
  - AD-3 Contract: exactly 16 fields preserved.

STATUS: FOR AUDIT ONLY — DO NOT PASTE INTO PROJECT YET.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ──────────────────────────────────────────────
# 1. BASE SCHEMA (shared fields)
# ──────────────────────────────────────────────
class RecommendationBase(BaseModel):
    """Shared DB-mapped fields between Create/Update/Response."""

    recommendation_id: str = Field(
        ...,
        description="Unique identifier. PK in SQLAlchemy."
    )
    case_id: str = Field(
        ...,
        description="FK to Case.case_id (CASCADE). NOT NULL in DB."
    )
    product_id: str = Field(
        ...,
        description="FK to Product.product_id (RESTRICT). NOT NULL in DB."
    )
    need_match_score: Optional[float] = Field(
        None,
        description="Match score from need analysis. Nullable in DB."
    )
    evidence_score: Optional[float] = Field(
        None,
        description="Evidence-based score. Nullable in DB."
    )
    eligibility_status: Optional[str] = Field(
        None,
        description="Eligibility status. Nullable in DB."
    )
    ranking_score: Optional[float] = Field(
        None,
        description="Ranking score. Nullable in DB."
    )
    ranking_reasons: Optional[str] = Field(
        None,
        description="Reasons for ranking. Nullable in DB."
    )


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    need_match_score: Optional[float] = Field(None, description="Update match score")
    evidence_score: Optional[float] = Field(None, description="Update evidence score")
    eligibility_status: Optional[str] = Field(None, description="Update eligibility status")
    ranking_score: Optional[float] = Field(None, description="Update ranking score")
    ranking_reasons: Optional[str] = Field(None, description="Update ranking reasons")


class RecommendationResponse(RecommendationBase):
    final_score: Optional[float] = Field(None, description="[AD-3 COMPUTED] Final aggregated score from Reasoning Engine.")
    confidence: Optional[float] = Field(None, description="[AD-3 COMPUTED] Confidence level of the recommendation.")
    eligibility: Optional[str] = Field(None, description="[AD-3 COMPUTED] Eligibility verdict.")
    reasoning: Optional[str] = Field(None, description="[AD-3 COMPUTED] Human-readable reasoning explanation.")
    evidence_refs: Optional[List[str]] = Field(None, description="[AD-3 COMPUTED] List of evidence references (claim_ids).")
    warnings: Optional[List[str]] = Field(None, description="[AD-3 COMPUTED] Warning messages from Framework 5 checks.")
    availability: Optional[str] = Field(None, description="[AD-3 DYNAMIC] Availability from Inventory layer.")
    price: Optional[int] = Field(None, description="[AD-3 DYNAMIC] Price in Toman from Inventory layer.")
    exclusion_reasons: Optional[str] = Field(None, description="[DB AUDIT] Exclusion reasons. Nullable in DB.")
    created_at: Optional[datetime] = Field(None, description="[DB AUDIT] Creation timestamp. server_default in DB.")
    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional structured details.")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class EvidenceCreate(BaseModel):
    product_id: str
    claim: str
    source_type: str
    source_reference: str
    claim_type: Optional[str] = "UNKNOWN"
    field: Optional[str] = None
    source_date: Optional[str] = None
    evidence_strength: Optional[str] = None
    market_region: Optional[str] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class EvidenceUpdate(BaseModel):
    claim: Optional[str] = None
    claim_type: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    source_date: Optional[str] = None
    evidence_strength: Optional[str] = None
    market_region: Optional[str] = None
    notes: Optional[str] = None
    qa_status: Optional[str] = None
    conflict_status: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class EvidenceResponse(BaseModel):
    evidence_id: str
    product_id: str
    claim_id: Optional[str] = None
    field: Optional[str] = None
    claim: Optional[str] = None
    claim_type: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    source_date: Optional[str] = None
    evidence_date: Optional[datetime] = None
    evidence_strength: Optional[str] = None
    evidence_status: Optional[str] = None
    conflict_status: Optional[str] = None
    market_region: Optional[str] = None
    notes: Optional[str] = None
    qa_status: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class VerifyRequest(BaseModel):
    verdict: str


class ResolveConflictRequest(BaseModel):
    resolution: str


class ProductKnowledgeResponse(BaseModel):
    product_knowledge_id: str
    product_id: str
    ingredients: Optional[str] = None
    ingredient_roles: Optional[str] = None
    claimed_benefits: Optional[str] = None
    known_use_cases: Optional[str] = None
    contraindications: Optional[str] = None
    usage_instructions: Optional[str] = None
    manufacturer_claims: Optional[str] = None
    evidence_refs: Optional[str] = None
    evidence_status: Optional[str] = None
    knowledge_confidence: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ConflictEntryResponse(BaseModel):
    field: Optional[str] = None
    values: List[str] = []
    evidence_ids: List[str] = []
    severity: str = "HIGH"
    status: str = "UNRESOLVED"


class ProductCreate(BaseModel):
    """P4 P0: client cannot inject lifecycle/governance state."""
    product_id: str
    brand: str
    product_name: str
    variant: Optional[str] = None
    size_value: Optional[float] = None
    size_unit: Optional[str] = None
    barcode_gtin: Optional[str] = None
    market_region: Optional[str] = None
    country_of_origin: Optional[str] = None
    packaging_version: Optional[str] = None
    category_id: Optional[str] = None


class ProductUpdate(BaseModel):
    """Informational fields only — governance fields forbidden (P4 P0)."""
    brand: Optional[str] = None
    product_name: Optional[str] = None
    variant: Optional[str] = None
    size_value: Optional[float] = None
    size_unit: Optional[str] = None
    barcode_gtin: Optional[str] = None
    market_region: Optional[str] = None
    country_of_origin: Optional[str] = None
    packaging_version: Optional[str] = None
    category_id: Optional[str] = None


class ProductTransitionRequest(BaseModel):
    reason: Optional[str] = None


class ProductRejectRequest(BaseModel):
    reason: str


class ProductQARequest(BaseModel):
    verdict: str
    notes: Optional[str] = None


class ProductIdentityVerifyRequest(BaseModel):
    identity_status: str
    source_refs: Optional[str] = None
    confidence: Optional[float] = None
