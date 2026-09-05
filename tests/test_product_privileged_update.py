"""P4 WP-01 — Explicit-intent guard on update_governance_privileged.

Reality Note: Existing coverage inspected in tests/test_product_compliance.py
before defining remaining scope (#15).

IMPORTANT: confirm_escape_hatch is a safety assertion / intentionality flag.
It is NOT AuthZ. A caller with repository access can still pass True.
"""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.models.product import Product
from app.models.user_role import ROLE_REVIEWER_QA
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.services.product_transition_service import ProductTransitionService


def _make_product(db, pid="P_WP01_001", status="DRAFT", **kwargs):
    p = Product(
        product_id=pid,
        brand=kwargs.get("brand", "BrandX"),
        product_name=kwargs.get("product_name", "NameY"),
        identity_status=kwargs.get("identity_status", "NEEDS_REVIEW"),
        qa_verdict=kwargs.get("qa_verdict", "PENDING"),
        status=status,
    )
    db.add(p)
    db.flush()
    return p


def test_privileged_without_explicit_intent_raises(db_session):
    """Bare call fails — intentionality guard, not AuthZ."""
    _make_product(db_session, "P_WP01_NOAUTH")
    repo = ProductRepository(db_session)
    with pytest.raises(ValidationError, match="confirm_escape_hatch=True"):
        repo.update_governance_privileged("P_WP01_NOAUTH", status="ACTIVE")


def test_privileged_with_explicit_intent_allows(db_session):
    """Passing confirm_escape_hatch=True is explicit intent — still not AuthZ."""
    _make_product(db_session, "P_WP01_AUTH")
    repo = ProductRepository(db_session)
    updated = repo.update_governance_privileged(
        "P_WP01_AUTH", confirm_escape_hatch=True, status="ACTIVE"
    )
    assert updated is not None
    assert updated.status == "ACTIVE"


def test_generic_repository_update_still_blocks_governance(db_session):
    _make_product(db_session, "P_WP01_GEN")
    with pytest.raises(ValidationError, match="Governance fields"):
        ProductRepository(db_session).update("P_WP01_GEN", status="ACTIVE")


def test_service_update_still_blocks_governance(db_session):
    _make_product(db_session, "P_WP01_SVC")
    with pytest.raises(ValidationError, match="Governance fields"):
        ProductService(db_session).update("P_WP01_SVC", qa_verdict="VALID")


def test_transition_service_lifecycle_still_works(db_session):
    """ProductTransitionService does not call update_governance_privileged."""
    _make_product(db_session, "P_WP01_LIFE")
    tr = ProductTransitionService(db_session)
    assert tr.submit("P_WP01_LIFE", "rev", {ROLE_REVIEWER_QA}).status == "SUBMITTED"
    assert tr.enter_qa_review("P_WP01_LIFE", "rev", {ROLE_REVIEWER_QA}).status == "QA_REVIEW"
