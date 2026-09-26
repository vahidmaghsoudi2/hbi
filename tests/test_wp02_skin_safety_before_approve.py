"""WP-02 — Skin safety minimum before APPROVE / ACTIVATE."""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.user_role import ROLE_PO
from app.services.product_transition_service import ProductTransitionService
from app.services.skin_safety_minimum_service import SkinSafetyMinimumService


def _product(db, pid, *, status="QA_REVIEW"):
    p = Product(
        product_id=pid,
        brand="SkinCo",
        product_name="Barrier Cream",
        status=status,
        qa_verdict="VALID",
        identity_status="VERIFIED",
    )
    db.add(p)
    db.flush()
    return p


def _ev(db, *, eid, pid, field=None, claim="x", claim_type="FACT", qa="VERIFIED", conflict="NONE"):
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


def _ready_unrelated(db, pid, eid="E_WP02_READY"):
    """Satisfies generic Evidence Readiness + D3 identity path without contraindications."""
    _ev(db, eid=eid, pid=pid, field="brand", claim="SkinCo", claim_type="FACT", qa="VERIFIED")


def test_approve_blocked_with_no_contraindications_evidence(db_session):
    pid = "WP02-NONE"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_approve_blocked_with_only_unrelated_verified_evidence(db_session):
    pid = "WP02-UNREL"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid, "E_WP02_U1")
    _ev(
        db_session,
        eid="E_WP02_U2",
        pid=pid,
        field="claimed_benefits",
        claim="hydration",
        claim_type="BENEFIT",
        qa="VERIFIED",
    )
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_approve_blocked_with_pending_contraindications(db_session):
    pid = "WP02-PEND"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_P",
        pid=pid,
        field="contraindications",
        claim="allergy risk",
        claim_type="MANUFACTURER_CLAIM",
        qa="PENDING",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False
    # PENDING also fails generic Evidence Readiness (runs before safety).
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_approve_blocked_with_unresolved_contraindications_conflict(db_session):
    pid = "WP02-CF"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_CF",
        pid=pid,
        field="contraindications",
        claim="pregnancy",
        claim_type="MANUFACTURER_CLAIM",
        qa="VERIFIED",
        conflict="CONFLICT",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_approve_allowed_with_verified_nonempty_contraindications(db_session):
    pid = "WP02-OK-CONTENT"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_OK",
        pid=pid,
        field="contraindications",
        claim="not for broken skin",
        claim_type="MANUFACTURER_CLAIM",
        qa="VERIFIED",
    )
    assert (
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO}).status
        == "APPROVED"
    )


def test_approve_allowed_with_explicit_unknown_verified(db_session):
    pid = "WP02-OK-UNK"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_UNK",
        pid=pid,
        field="contraindications",
        claim="UNKNOWN",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )
    assert (
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO}).status
        == "APPROVED"
    )


def test_unknown_on_other_field_does_not_satisfy(db_session):
    pid = "WP02-OTHER-UNK"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_OU",
        pid=pid,
        field="ingredients",
        claim="UNKNOWN",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})


def test_activate_repeats_safety_gate(db_session):
    pid = "WP02-ACT"
    _product(db_session, pid, status="APPROVED")
    _ready_unrelated(db_session, pid)
    with pytest.raises(ValidationError, match="Skin safety minimum"):
        ProductTransitionService(db_session).activate(pid, "po", {ROLE_PO})
    _ev(
        db_session,
        eid="E_WP02_ACT",
        pid=pid,
        field="contraindications",
        claim="UNKNOWN",
        claim_type="UNKNOWN",
        qa="VERIFIED",
    )
    assert (
        ProductTransitionService(db_session).activate(pid, "po", {ROLE_PO}).status
        == "ACTIVE"
    )


def test_rejected_contraindications_do_not_satisfy(db_session):
    pid = "WP02-REJ"
    _product(db_session, pid)
    _ready_unrelated(db_session, pid)
    _ev(
        db_session,
        eid="E_WP02_RJ",
        pid=pid,
        field="contraindications",
        claim="bad claim",
        claim_type="MANUFACTURER_CLAIM",
        qa="REJECTED",
    )
    assert SkinSafetyMinimumService(db_session).evaluate(pid).satisfied is False
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve(pid, "po", {ROLE_PO})
