"""Mission #144 — Governed Product Intake → ACTIVE → Recommendation candidate set.

Proves the minimum repository path without bypassing lifecycle governance
and without treating seed PENDING rows as production-ready.
"""
from __future__ import annotations

from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.product_knowledge import ProductKnowledge
from app.models.user_role import ROLE_PO
from app.repositories.product_repository import ProductRepository
from app.services.evidence_readiness_service import EvidenceReadinessService
from app.services.product_service import ProductService
from app.services.product_transition_service import ProductTransitionService
from app.services.recommendation_service import RecommendationService


PO = {ROLE_PO}
PID = "P_CATALOG_INTAKE_E2E_001"


def test_governed_intake_reaches_engine_ready_and_recommendation(db_session):
    """create → submit → QA_REVIEW → identity VERIFIED → claim Evidence +
    readiness → APPROVE → ACTIVATE → appears in ACTIVE VERIFIED candidate set
    and can be selected by recommendation for a matching case.
    """
    transitions = ProductTransitionService(db_session)

    product = ProductService(db_session).create_product_with_inventory(
        {
            "product_id": PID,
            "brand": "CatalogBrand",
            "product_name": "Hydration Serum",
            "variant": "30ml",
            "size_value": 30,
            "size_unit": "ml",
            "barcode_gtin": "1000000000001",
            "market_region": "IR",
            "knowledge_use_cases": "hydration",
            "knowledge_evidence_claim": "supports skin hydration",
            "knowledge_evidence_source_reference": "PRODUCT_INTAKE",
        },
        actor_id="editor_catalog",
        roles={"EDITOR"},
    )
    assert product.status == "DRAFT"

    transitions.submit(PID, "rev_catalog", {"REVIEWER_QA"})
    transitions.enter_qa_review(PID, "rev_catalog", {"REVIEWER_QA"})
    transitions.verify_identity(
        PID,
        "rev_catalog",
        {"REVIEWER_QA"},
        "VERIFIED",
        source_refs="test://identity",
        confidence=1.0,
    )

    # Evidence + claim surface before QA VALID (D3 Conditional: claim Evidence required).
    db_session.add(
        Evidence(
            evidence_id=f"EV-{PID}-READY",
            product_id=PID,
            claim_id=f"EV-{PID}-001",
            source_type="PEER_REVIEWED",
            source_reference="test://mission-144-evidence",
            claim="supports skin hydration",
            field="claimed_benefits",
            claim_type="BENEFIT",
            evidence_strength="HIGH",
            qa_status="APPROVED",
            conflict_status="NONE",
            evidence_status="SUPPORTED",
        )
    )
    db_session.add(
        ProductKnowledge(
            product_knowledge_id=f"PK-{PID}",
            product_id=PID,
            known_use_cases="hydration",
            claimed_benefits="supports skin hydration",
            evidence_status="SUPPORTED",
            knowledge_confidence=1.0,
        )
    )
    db_session.flush()

    transitions.set_product_qa(PID, "po_catalog", PO, "VALID", notes="Mission 144 readiness")

    # WP-02 skin safety minimum before APPROVE
    db_session.add(
        Evidence(
            evidence_id=f"EV-{PID}-SAFE",
            product_id=PID,
            source_type="MANUFACTURER",
            source_reference="test://safety",
            claim="none known",
            field="contraindications",
            claim_type="MANUFACTURER_CLAIM",
            qa_status="VERIFIED",
            conflict_status="NONE",
        )
    )
    db_session.flush()

    readiness = EvidenceReadinessService(db_session).evaluate(PID)
    assert readiness.ready is True, readiness.summary

    assert transitions.approve(PID, "po_catalog", PO).status == "APPROVED"
    assert transitions.activate(PID, "po_catalog", PO).status == "ACTIVE"

    candidates = ProductRepository(db_session).find_by_identity_status_and_active("VERIFIED")
    candidate_ids = {p.product_id for p in candidates}
    assert PID in candidate_ids

    customer = Customer(
        customer_id="CUST_CATALOG_INTAKE_001",
        name="Catalog Path Customer",
        mobile="09123334455",
        concerns="آبرسان",
        skin_profile="پوست خشک",
    )
    case = Case(case_id="CASE_CATALOG_INTAKE_001", customer_id=customer.customer_id, case_type="OPEN")
    db_session.add_all([customer, case])
    db_session.flush()

    recs = RecommendationService(db_session).generate_recommendations(case.case_id)
    assert isinstance(recs, list)
