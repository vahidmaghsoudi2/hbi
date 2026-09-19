"""D3 Controlled Hybrid Enforcement — Claim-Ready vs Engine-Ready."""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.user_role import ROLE_PO
from app.services.controlled_hybrid_policy import ControlledHybridPolicy
from app.services.product_transition_service import ProductTransitionService


PO = {ROLE_PO}


def _product(db, pid: str, status: str = "QA_REVIEW") -> None:
    db.add(
        Product(
            product_id=pid,
            brand="Hybrid",
            product_name=pid,
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status=status,
        )
    )
    db.flush()


def _ev(db, pid: str, eid: str, *, field: str, claim_type: str, qa: str = "APPROVED") -> None:
    db.add(
        Evidence(
            evidence_id=eid,
            product_id=pid,
            claim_id=f"{eid}-c",
            source_type="SECONDARY",
            source_reference="test://hybrid",
            claim=f"claim for {field}",
            field=field,
            claim_type=claim_type,
            qa_status=qa,
            conflict_status="NONE",
        )
    )
    db.flush()


def test_identity_only_is_claim_ready_not_engine_ready(db_session):
    pid = "P_HYB_ID_ONLY"
    _product(db_session, pid)
    _ev(db_session, pid, "E_ID", field="brand", claim_type="FACT")
    result = ControlledHybridPolicy(db_session).evaluate(pid)
    assert result.claim_ready is True
    assert result.engine_ready is False
    assert "E_ID" in result.identity_only_evidence_ids
    assert result.claim_evidence_ids == []


def test_benefit_claim_is_engine_ready(db_session):
    pid = "P_HYB_BENEFIT"
    _product(db_session, pid)
    _ev(db_session, pid, "E_B", field="claimed_benefits", claim_type="BENEFIT")
    result = ControlledHybridPolicy(db_session).evaluate(pid)
    assert result.claim_ready is True
    assert result.engine_ready is True
    assert "E_B" in result.claim_evidence_ids


def test_pending_blocks_claim_and_engine(db_session):
    pid = "P_HYB_PENDING"
    _product(db_session, pid)
    _ev(db_session, pid, "E_P", field="claimed_benefits", claim_type="BENEFIT", qa="PENDING")
    result = ControlledHybridPolicy(db_session).evaluate(pid)
    assert result.claim_ready is False
    assert result.engine_ready is False


def test_activate_blocked_when_identity_only(db_session):
    pid = "P_HYB_ACT_ID"
    _product(db_session, pid, status="APPROVED")
    _ev(db_session, pid, "E_ID2", field="brand", claim_type="FACT")
    with pytest.raises(ValidationError, match="Engine-Ready"):
        ProductTransitionService(db_session).activate(pid, "po", PO)


def test_activate_allowed_with_claim_evidence(db_session):
    pid = "P_HYB_ACT_OK"
    _product(db_session, pid, status="APPROVED")
    _ev(db_session, pid, "E_OK", field="claimed_benefits", claim_type="BENEFIT")
    product = ProductTransitionService(db_session).activate(pid, "po", PO)
    assert product.status == "ACTIVE"


def test_approve_still_allows_identity_only_claim_ready(db_session):
    """APPROVE uses Claim-Ready (existing EvidenceReadiness), not Engine-Ready."""
    pid = "P_HYB_APPR_ID"
    _product(db_session, pid, status="QA_REVIEW")
    _ev(db_session, pid, "E_AP", field="brand", claim_type="FACT")
    product = ProductTransitionService(db_session).approve(pid, "po", PO)
    assert product.status == "APPROVED"
