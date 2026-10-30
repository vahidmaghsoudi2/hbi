from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.models.base import Base


class ProductProblemLink(Base):
    """Immutable, evidence-anchored product-to-problem assessment record.

    V1 deliberately cannot persist SUPPORTED links. The first implementation
    records only CANDIDATE, NOT_LINKED, or DEFERRED assessments.
    """

    __tablename__ = "ProductProblemLink"

    link_id = Column(String, primary_key=True)
    product_id = Column(
        String,
        ForeignKey("Product.product_id", ondelete="RESTRICT"),
        nullable=False,
    )
    variant = Column(String, nullable=False, server_default="UNKNOWN")
    market_region = Column(String, nullable=False)
    claim_id = Column(
        String,
        ForeignKey("Evidence.claim_id", ondelete="RESTRICT"),
        nullable=False,
    )
    evidence_id = Column(
        String,
        ForeignKey("Evidence.evidence_id", ondelete="RESTRICT"),
        nullable=False,
    )
    problem_id = Column(String, nullable=False)
    problem_type = Column(String, nullable=False)
    problem_definition_ref = Column(String, nullable=False)
    relationship_role = Column(String, nullable=False)
    relationship_status = Column(String, nullable=False, server_default="CANDIDATE")
    semantic_basis = Column(String, nullable=False)
    limitations = Column(String, nullable=False)
    decision_basis = Column(String, nullable=False)
    problem_map_version = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    __table_args__ = (
        CheckConstraint(
            "variant IN ('COLOR', 'NON_COLOR', 'UNKNOWN')",
            name="ck_productproblemlink_variant",
        ),
        CheckConstraint(
            "relationship_role IN ('presentation', 'context', 'clinical_anchor', 'sequela')",
            name="ck_productproblemlink_role",
        ),
        CheckConstraint(
            "relationship_status IN ('CANDIDATE', 'NOT_LINKED', 'DEFERRED')",
            name="ck_productproblemlink_status",
        ),
        UniqueConstraint(
            "product_id",
            "evidence_id",
            "problem_id",
            "relationship_role",
            "variant",
            "market_region",
            name="uq_productproblemlink_evidence_problem_scope",
        ),
        Index("ix_productproblemlink_product", "product_id"),
        Index("ix_productproblemlink_problem", "problem_id"),
        Index("ix_productproblemlink_status", "relationship_status"),
    )
