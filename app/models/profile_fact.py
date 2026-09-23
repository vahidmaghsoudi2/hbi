"""Customer Profile Fact — versioned, consent-gated reusable customer knowledge."""
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


PROFILE_FACT_KEYS = frozenset({
    "skin_profile",
    "hair_profile",
    "scalp_profile",
    "age_range",
    "concerns",
})
VALUE_STATES = frozenset({"KNOWN", "UNKNOWN", "PREFER_NOT_TO_SAY", "NOT_APPLICABLE"})
PROVENANCES = frozenset({"CUSTOMER", "SELLER", "SYSTEM", "IMPORTED"})
STATUSES = frozenset({"ACTIVE", "STALE", "SUPERSEDED", "REVOKED", "CONFLICTED"})


class ProfileFact(Base):
    __tablename__ = "ProfileFact"

    profile_fact_id = Column(String, primary_key=True)
    customer_id = Column(
        String,
        ForeignKey("Customer.customer_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attribute_key = Column(String, nullable=False)
    value = Column(Text, nullable=True)
    value_state = Column(String, nullable=False)
    provenance = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default="ACTIVE")
    supersedes_fact_id = Column(
        String,
        ForeignKey("ProfileFact.profile_fact_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    __table_args__ = (
        CheckConstraint(
            "attribute_key IN ('skin_profile', 'hair_profile', 'scalp_profile', 'age_range', 'concerns')",
            name="ck_profile_fact_attribute_key",
        ),
        CheckConstraint(
            "value_state IN ('KNOWN', 'UNKNOWN', 'PREFER_NOT_TO_SAY', 'NOT_APPLICABLE')",
            name="ck_profile_fact_value_state",
        ),
        CheckConstraint(
            "provenance IN ('CUSTOMER', 'SELLER', 'SYSTEM', 'IMPORTED')",
            name="ck_profile_fact_provenance",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'STALE', 'SUPERSEDED', 'REVOKED', 'CONFLICTED')",
            name="ck_profile_fact_status",
        ),
        CheckConstraint(
            "(value_state = 'KNOWN' AND value IS NOT NULL AND length(trim(value)) > 0) "
            "OR (value_state <> 'KNOWN')",
            name="ck_profile_fact_known_value",
        ),
    )

    customer = relationship("Customer", back_populates="profile_facts")
    superseded_fact = relationship(
        "ProfileFact",
        remote_side=[profile_fact_id],
        foreign_keys=[supersedes_fact_id],
        uselist=False,
    )
