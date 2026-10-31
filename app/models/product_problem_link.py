from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String,
    Text, UniqueConstraint,
)
from sqlalchemy.sql import func

from app.models.base import Base


class ProductProblemLink(Base):
    """Append-only assessment revisions; SUPPORTED is intentionally unavailable."""

    __tablename__ = "ProductProblemLink"

    link_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)
    variant = Column(String, nullable=False, server_default="UNKNOWN")
    market_region = Column(String, nullable=False)
    claim_id = Column(String, ForeignKey("Evidence.claim_id", ondelete="RESTRICT"), nullable=False)
    evidence_id = Column(String, ForeignKey("Evidence.evidence_id", ondelete="RESTRICT"), nullable=False)
    problem_id = Column(String, nullable=False)
    problem_type = Column(String, nullable=False)
    problem_definition_ref = Column(String, nullable=False)
    relationship_role = Column(String, nullable=False)
    relationship_status = Column(String, nullable=False, server_default="CANDIDATE")
    # Legacy rows keep NULL. New assessments must provide both fields explicitly.
    feature_basis = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    semantic_basis = Column(Text, nullable=False)
    limitations = Column(Text, nullable=False)
    decision_basis = Column(Text, nullable=False)
    problem_map_version = Column(String, nullable=False)
    assertion_key = Column(String, nullable=True)
    revision_no = Column(Integer, nullable=True)
    supersedes_link_id = Column(
        String, ForeignKey("ProductProblemLink.link_id", ondelete="RESTRICT"), nullable=True
    )
    idempotency_key = Column(String, nullable=True)
    request_fingerprint = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("variant IN ('COLOR', 'NON_COLOR', 'UNKNOWN')", name="ck_productproblemlink_variant"),
        CheckConstraint("relationship_role IN ('presentation', 'context', 'clinical_anchor', 'sequela')", name="ck_productproblemlink_role"),
        CheckConstraint("relationship_status IN ('CANDIDATE', 'NOT_LINKED', 'DEFERRED')", name="ck_productproblemlink_status"),
        CheckConstraint("revision_no IS NULL OR revision_no >= 1", name="ck_productproblemlink_revision"),
        UniqueConstraint("assertion_key", "revision_no", name="uq_productproblemlink_assertion_revision"),
        UniqueConstraint("idempotency_key", name="uq_productproblemlink_idempotency"),
        UniqueConstraint("supersedes_link_id", name="uq_productproblemlink_successor"),
        Index("ix_productproblemlink_product", "product_id"),
        Index("ix_productproblemlink_problem", "problem_id"),
        Index("ix_productproblemlink_status", "relationship_status"),
        Index("ix_productproblemlink_assertion", "assertion_key"),
    )
