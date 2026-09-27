"""Mission #283 / WP-02 — Product Line scoped Skin Safety Minimum."""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.services.product_transition_service import ProductTransitionService
from app.services.skin_safety_minimum_service import SkinSafetyMinimumService
from app.models.user_role import ROLE_PO


def _product(db, pid, *, product_line="SKIN", status="QA_REVIEW"):
    p = Product(
        product_id=pid,
        brand="SkinCo",
        product_name="Barrier Cream",
        status=status,
        qa_verdict="VALID",
        identity_status="VERIFIED",
        product_line=product_line,
    )
    db.add(p)
    db.flush()
    return p


def _ev(
    db,
    *,
    eid,
    pid,
    field=None,
    claim="x",
    claim_type="FACT",
    qa="VERIFIED",
    conflict="NONE",
):
    db.add(
        Evidence(
            evidence_id=eid,
            product_id=pid,
            source_type="PEER_REVIEWED",
            source_reference="test://wp02",
            claim=claim,
            field=field,
            claim_type=claim_type,
            qa_status=qa,
            conflict_status=conflict,
        )
    )
    db.flush()


def _ready(db, pid, eid):
    _ev(
        db,
        eid=eid,
        pid=pid,
        field="brand",
        claim="SkinCo",
        claim_type="FACT",
        qa="VERIFIED",
    )


def test_skin_missing_contraindications_blocks_approve(db_session):
    pid = "WP02-SKIN-MISSING"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-MISSING-READY")

    result = SkinSafetyMinimumService(db_session).evaluate(pid)
    assert result.satisfied is False
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_skin_verified_contraindication_allows_approve(db_session):
    pid = "WP02-SKIN-VALID"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-VALID-READY")
    _ev(
        db_session,
        eid="E-SKIN-VALID-SAFE",
        pid=pid,
        field="contraindications",
        claim="do not use on broken skin",
        claim_type="MANUFACTURER_CLAIM",
        qa="VERIFIED",
    )

    result = SkinSafetyMinimumService(db_session).evaluate(pid)
    assert result.satisfied is True
    assert "E-SKIN-VALID-SAFE" in result.matching_evidence_ids
    assert ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO}).status == "APPROVED"


def test_skin_explicit_unknown_allows_approve(db_session):
    pid = "WP02-SKIN-UNKNOWN"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-UNKNOWN-READY")
    _ev(
        db_session,
        eid="E-SKIN-UNKNOWN-SAFE",
        pid=pid,
        field="contraindications",
        claim="",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )

    result = SkinSafetyMinimumService(db_session).evaluate(pid)
    assert result.satisfied is True
    assert "E-SKIN-UNKNOWN-SAFE" in result.matching_evidence_ids
    assert ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO}).status == "APPROVED"


@pytest.mark.parametrize("qa", ["PENDING", "NEEDS_REVIEW", "REJECTED"])
def test_skin_untrusted_contraindication_does_not_satisfy(db_session, qa):
    pid = f"WP02-SKIN-{qa}"
    _product(db_session, pid)
    _ready(db_session, pid, f"E-{pid}-READY")
    _ev(
        db_session,
        eid=f"E-{pid}-SAFE",
        pid=pid,
        field="contraindications",
        claim="risk",
        claim_type="MANUFACTURER_CLAIM",
        qa=qa,
    )
    result = SkinSafetyMinimumService(db_session).evaluate(pid)
    assert result.satisfied is False


def test_skin_conflicting_contraindication_does_not_satisfy(db_session):
    pid = "WP02-SKIN-CONFLICT"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-CONFLICT-READY")
    _ev(
        db_session,
        eid="E-SKIN-CONFLICT-SAFE",
        pid=pid,
        field="contraindications",
        claim="conflicting risk statement",
        claim_type="MANUFACTURER_CLAIM",
        qa="VERIFIED",
        conflict="CONFLICT",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False


def test_skin_claim_type_conflict_does_not_satisfy(db_session):
    pid = "WP02-SKIN-CLAIMTYPE-CONFLICT"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-CLAIMTYPE-CONFLICT-READY")
    _ev(
        db_session,
        eid="E-SKIN-CLAIMTYPE-CONFLICT-SAFE",
        pid=pid,
        field="contraindications",
        claim="conflicting statement",
        claim_type="CONFLICT",
        qa="VERIFIED",
        conflict="NONE",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_skin_empty_contraindication_does_not_mean_safe(db_session):
    pid = "WP02-SKIN-EMPTY"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-EMPTY-READY")
    _ev(
        db_session,
        eid="E-SKIN-EMPTY-SAFE",
        pid=pid,
        field="contraindications",
        claim="",
        claim_type="FACT",
        qa="VERIFIED",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False


def test_unknown_on_other_field_does_not_satisfy(db_session):
    pid = "WP02-SKIN-OTHER-UNKNOWN"
    _product(db_session, pid)
    _ready(db_session, pid, "E-SKIN-OTHER-UNKNOWN-READY")
    _ev(
        db_session,
        eid="E-SKIN-OTHER-UNKNOWN",
        pid=pid,
        field="ingredients",
        claim="",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False


def test_non_skin_is_not_forced_through_skin_gate(db_session):
    pid = "WP02-HAIR-NO-SAFETY"
    _product(db_session, pid, product_line="HAIR")
    _ready(db_session, pid, "E-HAIR-READY")

    result = SkinSafetyMinimumService(db_session).evaluate(pid)
    assert result.satisfied is True
    assert "NOT_APPLICABLE" in result.summary

    assert ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO}).status == "APPROVED"


def test_activate_rechecks_skin_safety(db_session):
    pid = "WP02-SKIN-ACTIVATE"
    _product(db_session, pid, status="APPROVED")
    _ready(db_session, pid, "E-SKIN-ACTIVATE-READY")

    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).activate(pid, "po", {ROLE_PO})

    _ev(
        db_session,
        eid="E-SKIN-ACTIVATE-SAFE",
        pid=pid,
        field="contraindications",
        claim="UNKNOWN",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )
    assert ProductTransitionService(db_session).activate(pid, "po", {ROLE_PO}).status == "ACTIVE"


def test_existing_hair_path_preserves_activation_behavior(db_session):
    pid = "WP02-HAIR-ACTIVATE"
    _product(db_session, pid, product_line="HAIR", status="APPROVED")
    _ready(db_session, pid, "E-HAIR-ACTIVATE-READY")
    assert ProductTransitionService(db_session).activate(pid, "po", {ROLE_PO}).status == "ACTIVE"
