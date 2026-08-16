from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ProductDTO:
    product_id: str
    brand: str
    product_name: str
    identity_status: str
    qa_verdict: str
    variant: Optional[str] = None
    size_value: Optional[float] = None
    size_unit: Optional[str] = None

@dataclass
class CustomerDTO:
    customer_id: str
    name: str
    mobile: Optional[str] = None
    consent_to_store_data: int = 0

@dataclass
class CaseDTO:
    case_id: str
    customer_id: str
    case_type: str

@dataclass
class RecommendationDTO:
    recommendation_id: str
    case_id: str
    product_id: str
    need_match_score: Optional[float] = None
    eligibility_status: Optional[str] = None
    ranking_score: Optional[float] = None
    ranking_reasons: Optional[str] = None
    # AD-3 Contract fields
    final_score: Optional[float] = None
    confidence: Optional[float] = None
    eligibility: Optional[str] = None
    reasoning: Optional[str] = None
    evidence_score: Optional[float] = None
    evidence_refs: Optional[list] = None
    warnings: Optional[list] = None
    availability: Optional[str] = None
    price: Optional[int] = None

@dataclass
class InventoryDTO:
    inventory_id: str
    product_id: str
    quantity_available: int
    quantity_reserved: int
    stock_status: str
    sale_price_toman: Optional[int] = None

@dataclass
class SaleItemDTO:
    sale_item_id: str
    sale_id: str
    product_id: str
    quantity: int
    unit_price_toman: int

@dataclass
class SaleDTO:
    sale_id: str
    customer_id: str
    total_amount_toman: int
    items: Optional[List[SaleItemDTO]] = None

# ─── Evidence & ProductKnowledge DTOs (Phase 3) ─────────────────

@dataclass
class EvidenceDTO:
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


@dataclass
class ProductKnowledgeDTO:
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


@dataclass
class ConflictEntryDTO:
    field: Optional[str] = None
    values: List[str] = None
    evidence_ids: List[str] = None
    severity: str = "HIGH"
    status: str = "UNRESOLVED"
