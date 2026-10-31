from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


RelationshipRole = Literal["presentation", "context", "clinical_anchor", "sequela"]
RelationshipStatus = Literal["CANDIDATE", "NOT_LINKED", "DEFERRED"]
Variant = Literal["COLOR", "NON_COLOR", "UNKNOWN"]


class ProductProblemLinkCreate(BaseModel):
    product_id: str = Field(min_length=1, max_length=128)
    evidence_id: str = Field(min_length=1, max_length=128)
    claim_id: str = Field(min_length=1, max_length=128)
    problem_id: str = Field(min_length=3, max_length=3, pattern=r"^P\d{2}$")
    problem_type: str = Field(min_length=1, max_length=128)
    problem_definition_ref: str = Field(min_length=1, max_length=512)
    relationship_role: RelationshipRole
    relationship_status: RelationshipStatus
    feature_basis: str = Field(min_length=1, max_length=4000)
    outcome: str = Field(min_length=1, max_length=2000)
    semantic_basis: str = Field(min_length=1, max_length=4000)
    limitations: str = Field(min_length=1, max_length=4000)
    decision_basis: str = Field(min_length=1, max_length=4000)
    reason: str = Field(min_length=1, max_length=2000)
    idempotency_key: str = Field(min_length=8, max_length=128)
    problem_map_version: str = Field(default="SKIN_PROBLEM_SPACE_MAP_V0.1", min_length=1, max_length=128)
    variant: Variant = "UNKNOWN"
    market_region: str = Field(min_length=1, max_length=64)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProductProblemLinkReassess(ProductProblemLinkCreate):
    expected_revision_no: Optional[int] = Field(default=None, ge=1)


class ProductProblemLinkResponse(BaseModel):
    link_id: str
    product_id: str
    variant: str
    market_region: str
    claim_id: str
    evidence_id: str
    problem_id: str
    problem_type: str
    problem_definition_ref: str
    relationship_role: str
    relationship_status: str
    feature_basis: Optional[str] = None
    outcome: Optional[str] = None
    semantic_basis: str
    limitations: str
    decision_basis: str
    problem_map_version: str
    assertion_key: Optional[str] = None
    revision_no: Optional[int] = None
    supersedes_link_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
