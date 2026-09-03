"""P4 P0 — Server-side role mapping. Client-supplied roles are not authoritative."""
from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base

ROLE_EDITOR = "Editor"
ROLE_REVIEWER_QA = "Reviewer/QA"
ROLE_PO = "PO"
ROLE_ADMIN = "Admin"

VALID_ROLES = frozenset({ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN})


class UserRole(Base):
    __tablename__ = "UserRole"

    user_role_id = Column(String, primary_key=True)
    subject_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        UniqueConstraint("subject_id", "role", name="uq_userrole_subject_role"),
    )
