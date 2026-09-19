"""Mission HBI-D3-CONDITIONAL-EVIDENCE-POLICY-001 — executable D3 Conditional rules."""
from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.user_role import ROLE_PO
from app.services.d3_conditional_evidence_policy import D3ConditionalEvidencePolicy
from app.services.product_transition_service import ProductTransitionService

PO = {ROLE_PO}


def _product(db, pid, **kwargs):
    p = Product(
        product_id=pid,
        brand=kwargs.get("brand", "Brand"),
        product_name=kwargs.get("product_name", "Name"),
        identity_status=kwargs.get("identity_status", "VERIFIED"),
        qa_verdict=kwargs.get("qa_verdict", "PENDING"),
        status=kwargs.get("status", "QA_REVIEW"),
    )
    db.add(p)
    db.flush()
    return p


def test_d3_identity_only_product_allows_valid_with_brand_evidence(db_session):
    pid = "P_D3_ID_ONLY"
    _product(db_session, pid)
    db_session.add(
        Evidence(
            evidence_id=f"EV-{pid}-B",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="SECONDARY",
            source_reference="record",
            claim="brand is Brand",
            field="brand",
            claim_type="FACT",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    db_session.flush()
    result = D3ConditionalEvidencePolicy(db_session).evaluate_for_qa_valid(pid)
    assert result.allowed is True
    assert result.has_performance_claims is False
    ProductTransitionService(db_session).set_product_qa(pid, "po", PO, "VALID")
    assert db_session.get(Product, pid).qa_verdict == "VALID"


def test_d3_claim_surface_blocks_valid_with_only_identity_evidence(db_session):
    pid = "P_D3_CLAIM_BLOCK"
    _product(db_session, pid)
    db_session.add(
        ProductKnowledge(
            product_knowledge_id=f"PK-{pid}",
            product_id=pid,
            known_use_cases="ضدآفتاب روزانه صورت",
        )
    )
    db_session.add(
        Evidence(
            evidence_id=f"EV-{pid}-B",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="SECONDARY",
            source_reference="record",
            claim="brand is Brand",
            field="brand",
            claim_type="FACT",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    db_session.flush()
    result = D3ConditionalEvidencePolicy(db_session).evaluate_for_qa_valid(pid)
    assert result.allowed is False
    assert result.has_performance_claims is True
    with pytest.raises(ValidationError, match="D3"):
        ProductTransitionService(db_session).set_product_qa(pid, "po", PO, "VALID")


def test_d3_claim_surface_allows_valid_with_claim_evidence(db_session):
    pid = "P_D3_CLAIM_OK"
    _product(db_session, pid)
    db_session.add(
        ProductKnowledge(
            product_knowledge_id=f"PK-{pid}",
            product_id=pid,
            known_use_cases="sun protection",
            claimed_benefits="UV protection",
        )
    )
    db_session.add_all(
        [
            Evidence(
                evidence_id=f"EV-{pid}-B",
                product_id=pid,
                claim_id=f"EV-{pid}-001",
                source_type="SECONDARY",
                source_reference="record",
                claim="brand is Brand",
                field="brand",
                claim_type="FACT",
                qa_status="APPROVED",
                conflict_status="NONE",
            ),
            Evidence(
                evidence_id=f"EV-{pid}-U",
                product_id=pid,
                claim_id=f"EV-{pid}-002",
                source_type="PEER_REVIEWED",
                source_reference="lab",
                claim="supports sun protection",
                field="known_use_cases",
                claim_type="BENEFIT",
                qa_status="APPROVED",
                conflict_status="NONE",
            ),
        ]
    )
    db_session.flush()
    result = D3ConditionalEvidencePolicy(db_session).evaluate_for_qa_valid(pid)
    assert result.allowed is True
    assert result.has_performance_claims is True
    assert f"EV-{pid}-U" in result.claim_evidence_ids
    ProductTransitionService(db_session).set_product_qa(pid, "po", PO, "VALID")
    assert db_session.get(Product, pid).qa_verdict == "VALID"


def test_d3_approve_enforces_same_gate(db_session):
    pid = "P_D3_APPROVE"
    _product(db_session, pid, qa_verdict="VALID", status="QA_REVIEW")
    db_session.add(
        ProductKnowledge(
            product_knowledge_id=f"PK-{pid}",
            product_id=pid,
            known_use_cases="hydration",
        )
    )
    db_session.add(
        Evidence(
            evidence_id=f"EV-{pid}-B",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="SECONDARY",
            source_reference="record",
            claim="brand is Brand",
            field="brand",
            claim_type="FACT",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    db_session.flush()
    with pytest.raises(ValidationError, match="D3"):
        ProductTransitionService(db_session).approve(pid, "po", PO)
