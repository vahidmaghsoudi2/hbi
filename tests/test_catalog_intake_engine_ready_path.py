"""Catalog / intake path — product must include product_line on create (Product Line V1)."""
from __future__ import annotations

from app.models.user_role import ROLE_PO
from app.services.product_service import ProductService
from app.services.product_transition_service import ProductTransitionService

PID = "CAT-INTAKE-PL-001"
PO = {ROLE_PO}


def test_catalog_intake_engine_ready_path(db_session):
    """create → submit → QA_REVIEW → identity VERIFIED → claim Evidence +
    ProductKnowledge → QA VALID → readiness → APPROVE → ACTIVATE → rec.
    """
    svc = ProductService(db_session)
    transitions = ProductTransitionService(db_session)

    product = svc.create_product_with_inventory(
        {
            "product_id": PID,
            "brand": "Catalog Test",
            "product_name": "Hydration Intake Path Product",
            "product_line": "SKIN",
        },
        actor_id="po_catalog",
        roles=PO,
    )
    assert product.status == "DRAFT"
    assert product.qa_verdict == "PENDING"
    assert product.identity_status == "NEEDS_REVIEW"
    assert product.product_line == "SKIN"
