from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.core.auth import create_access_token
from app.models.evidence import Evidence
from app.models.evidence_mutation_log import EvidenceMutationLog
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_mutation_log import ProductMutationLog
from app.models.user_role import ROLE_PO, UserRole
from app.services.acceptance_report_service import build_acceptance_reports


def _product(product_id: str, *, market_region="US") -> Product:
    return Product(
        product_id=product_id,
        brand="HBI Test",
        product_name=f"Acceptance Test {product_id}",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="DRAFT",
        market_region=market_region,
        packaging_version="PKG-2",
    )


def _po_headers(db_session):
    db_session.add(UserRole(
        user_role_id="UR-ACCEPTANCE-PO",
        subject_id="acceptance-po",
        role=ROLE_PO,
    ))
    db_session.commit()
    token = create_access_token({"sub": "acceptance-po"})
    return {"Authorization": f"Bearer {token}"}


def test_acceptance_report_applies_phase0_policy_and_separates_stored_from_verified(client, db_session):
    product_id = "AR-POLICY-001"
    product = _product(product_id)
    evidence = Evidence(
        evidence_id="EV-AR-POLICY-001",
        product_id=product_id,
        claim_id="CL-AR-POLICY-001",
        source_type="MANUFACTURER",
        source_reference="https://manufacturer.example/product",
        claim="Contains glycerin",
        field="ingredients",
        claim_type="MANUFACTURER_CLAIM",
        market_region="US",
        conflict_status="NONE",
        qa_status="VERIFIED",
    )
    knowledge = ProductKnowledge(
        product_knowledge_id="PK-AR-POLICY-001",
        product_id=product_id,
        ingredients="glycerin",
        contraindications="avoid eye area",
        evidence_refs='["CL-AR-POLICY-001"]',
        evidence_status="SUPPORTED",
        knowledge_confidence=0.8,
    )
    evidence_audit = EvidenceMutationLog(
        log_id="EML-AR-POLICY-001",
        timestamp=datetime(2026, 11, 15, tzinfo=timezone.utc),
        actor_id="reviewer-1",
        actor_role="Reviewer/QA",
        action="VERIFY",
        target_entity="Evidence",
        target_id=evidence.evidence_id,
        product_id=product_id,
        after_state=json.dumps({"qa_status": "VERIFIED"}),
        reason=None,
        resulting_state="VERIFIED",
    )
    product_audit = ProductMutationLog(
        log_id="PML-AR-POLICY-001",
        timestamp=datetime(2026, 11, 15, tzinfo=timezone.utc),
        actor_id="po-1",
        actor_role="PO",
        action="QA_CHANGE",
        target_entity="Product",
        target_id=product_id,
        after_state=json.dumps({"qa_verdict": "VALID", "qa_notes": "Reviewed"}),
        reason=None,
        resulting_state="DRAFT",
    )
    db_session.add_all([product, evidence, knowledge, evidence_audit, product_audit])
    db_session.commit()

    reports, audit_tables, errors = build_acceptance_reports(db_session, [product_id])

    assert errors == {}
    assert audit_tables == {"evidence": True, "product": True}
    report = reports[product_id]
    assert report["evidence_readiness"] == "BLOCKED"
    assert report["evidence_summary"]["verified"] == 1
    assert report["evidence_summary"]["eligible"] == 0
    assert report["evidence_summary"]["unknown_scope"] == 1
    item = report["evidence"][0]
    assert item["eligible"] is False
    assert "EVIDENCE_VERSION_SCOPE_UNAVAILABLE" in item["eligibility_reasons"]
    assert item["latest_qa_decision"]["actor"] == "reviewer-1"
    assert item["latest_qa_decision"]["reason_status"] == "MISSING"
    assert item["qa_decision_history_status"] == "INCOMPLETE"
    assert any("no matching per-row QA decision audit record" in note for note in report["limitations"])
    assert report["product"]["product_qa"]["latest_qa_decision"]["qa_notes"] == "Reviewed"
    assert report["product"]["product_qa"]["latest_qa_decision"]["reason_status"] == "MISSING"
    assert report["knowledge"]["stored_content_fields"] == ["ingredients", "contraindications"]
    assert report["knowledge"]["verified_content_fields"] == []
    assert report["knowledge"]["contraindications_status"] == "UNVERIFIED"
    assert report["data_availability"]["product_version_proves_evidence_scope"] is False


def test_approved_null_conflict_and_unknown_market_are_ineligible(db_session):
    product_id = "AR-UNKNOWN-001"
    db_session.add(_product(product_id, market_region=None))
    db_session.add(Evidence(
        evidence_id="EV-AR-UNKNOWN-001",
        product_id=product_id,
        source_type="MANUFACTURER",
        source_reference="source-1",
        claim="Claim",
        field="ingredients",
        claim_type="MANUFACTURER_CLAIM",
        market_region=None,
        conflict_status=None,
        qa_status="APPROVED",
    ))
    db_session.commit()

    reports, _, errors = build_acceptance_reports(db_session, [product_id])

    assert errors == {}
    item = reports[product_id]["evidence"][0]
    assert item["eligible"] is False
    assert "QA_STATUS_NOT_VERIFIED" in item["eligibility_reasons"]
    assert "CONFLICT_STATUS_UNKNOWN" in item["eligibility_reasons"]
    assert "MARKET_SCOPE_UNKNOWN" in item["eligibility_reasons"]
    assert "EVIDENCE_VERSION_SCOPE_UNAVAILABLE" in item["eligibility_reasons"]


def test_market_mismatch_is_reported_as_mixed_scope(db_session):
    product_id = "AR-MIXED-001"
    db_session.add(_product(product_id, market_region="US"))
    db_session.add(Evidence(
        evidence_id="EV-AR-MIXED-001",
        product_id=product_id,
        source_type="MANUFACTURER",
        source_reference="source-1",
        claim="Claim",
        field="ingredients",
        claim_type="MANUFACTURER_CLAIM",
        market_region="UK",
        conflict_status="NONE",
        qa_status="VERIFIED",
    ))
    db_session.commit()

    reports, _, errors = build_acceptance_reports(db_session, [product_id])

    assert errors == {}
    item = reports[product_id]["evidence"][0]
    assert item["scope_status"] == "MIXED"
    assert "MARKET_SCOPE_MISMATCH" in item["eligibility_reasons"]


@pytest.mark.parametrize("size", [100, 500])
def test_cohort_acceptance_report_scales_and_preserves_count_invariants(client, db_session, size):
    headers = _po_headers(db_session)
    ids = [f"AR-BULK-{size}-{index:03d}" for index in range(size)]
    db_session.add_all([_product(product_id) for product_id in ids])
    db_session.commit()

    response = client.post(
        "/api/v1/acceptance-reports/cohort",
        headers=headers,
        json={"cohort_label": f"bulk-{size}", "product_ids": ids},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["report_status"] == "COMPLETED"
    assert body["requested"] == size
    assert body["found"] == size
    assert body["missing"] == 0
    assert body["successfully_reported"] == size
    assert body["failed"] == 0
    assert body["not_assessed"] == size
    assert body["requested"] == body["found"] + body["missing"]
    assert body["found"] == body["successfully_reported"] + body["failed"]
    assert body["successfully_reported"] == (
        body["ready"] + body["partial"] + body["blocked"] + body["not_assessed"]
    )


def test_single_product_endpoint_is_read_only_and_requires_qa_role(client, db_session):
    product_id = "AR-READONLY-001"
    db_session.add(_product(product_id))
    db_session.commit()

    denied = client.get(f"/api/v1/products/{product_id}/acceptance-report")
    assert denied.status_code in (401, 403)

    headers = _po_headers(db_session)
    before_products = db_session.query(Product).count()
    before_evidence = db_session.query(Evidence).count()
    before_evidence_audit = db_session.query(EvidenceMutationLog).count()
    before_product_audit = db_session.query(ProductMutationLog).count()

    response = client.get(
        f"/api/v1/products/{product_id}/acceptance-report",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["product"]["product_id"] == product_id
    assert response.json()["evidence_readiness"] == "NOT_ASSESSED"
    assert db_session.query(Product).count() == before_products
    assert db_session.query(Evidence).count() == before_evidence
    assert db_session.query(EvidenceMutationLog).count() == before_evidence_audit
    assert db_session.query(ProductMutationLog).count() == before_product_audit


def test_cohort_rejects_duplicate_ids_and_reports_missing_products(client, db_session):
    headers = _po_headers(db_session)
    duplicate = client.post(
        "/api/v1/acceptance-reports/cohort",
        headers=headers,
        json={"product_ids": ["P1", "P1"]},
    )
    assert duplicate.status_code == 422

    response = client.post(
        "/api/v1/acceptance-reports/cohort",
        headers=headers,
        json={"product_ids": ["AR-MISSING-001"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["report_status"] == "COMPLETED_WITH_ERRORS"
    assert body["requested"] == 1
    assert body["found"] == 0
    assert body["missing"] == 1
    assert body["missing_product_ids"] == ["AR-MISSING-001"]


def test_conflict_resolution_side_effect_without_per_row_qa_audit_is_disclosed(db_session):
    product_id = "AR-AUDIT-GAP-001"
    db_session.add(_product(product_id))
    db_session.add(Evidence(
        evidence_id="EV-AR-AUDIT-GAP-001",
        product_id=product_id,
        source_type="MANUFACTURER",
        source_reference="source-1",
        claim="Competing claim rejected by conflict resolution",
        field="ingredients",
        claim_type="MANUFACTURER_CLAIM",
        market_region="US",
        conflict_status="NONE",
        qa_status="REJECTED",
        notes="[REJECTED_BY_CONFLICT_RESOLUTION winner=EV-WINNER] resolution note",
    ))
    db_session.commit()

    reports, _, errors = build_acceptance_reports(db_session, [product_id])

    assert errors == {}
    item = reports[product_id]["evidence"][0]
    assert item["qa_decision_history"] == []
    assert item["qa_decision_history_status"] == "INCOMPLETE"
    assert any("no matching per-row QA decision audit record" in note for note in reports[product_id]["limitations"])


def test_invalid_claim_type_is_not_eligible(db_session):
    product_id = "AR-CLAIM-TAXONOMY-001"
    db_session.add(_product(product_id))
    db_session.add(Evidence(
        evidence_id="EV-AR-CLAIM-TAXONOMY-001",
        product_id=product_id,
        source_type="MANUFACTURER",
        source_reference="source-1",
        claim="Claim",
        field="ingredients",
        claim_type="MADE_UP_TYPE",
        market_region="US",
        conflict_status="NONE",
        qa_status="VERIFIED",
    ))
    db_session.commit()

    reports, _, errors = build_acceptance_reports(db_session, [product_id])

    assert errors == {}
    item = reports[product_id]["evidence"][0]
    assert item["eligible"] is False
    assert "CLAIM_TYPE_INVALID" in item["eligibility_reasons"]
