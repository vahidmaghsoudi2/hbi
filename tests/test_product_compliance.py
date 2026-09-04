"""P4 P0 Product compliance — B1–B7, transitions, mutation log, readiness."""
from __future__ import annotations
import pytest
from app.models.product import Product
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA
from app.models.evidence import Evidence
from app.core.auth import create_access_token
from app.core.exceptions import ValidationError
from app.services.product_service import ProductService
from app.services.product_transition_service import ProductTransitionService
from app.services.mutation_log_service import MutationLogService
from app.services.evidence_readiness_service import EvidenceReadinessService
from app.repositories.product_repository import ProductRepository
from app.interface.schemas import ProductCreate, ProductUpdate


def _seed_role(db, subject_id, role, rid):
    db.add(UserRole(user_role_id=rid, subject_id=subject_id, role=role))
    db.flush()


def _auth_header(subject_id):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject_id})}"}


def _make_product(db, pid="P_CMP_001", status="DRAFT", **kwargs):
    p = Product(
        product_id=pid, brand=kwargs.get("brand", "BrandX"),
        product_name=kwargs.get("product_name", "NameY"),
        identity_status=kwargs.get("identity_status", "NEEDS_REVIEW"),
        qa_verdict=kwargs.get("qa_verdict", "PENDING"), status=status,
    )
    db.add(p)
    db.flush()
    return p


def test_product_create_forces_draft(db_session):
    p = ProductService(db_session).create_product_with_inventory(
        {"product_id": "P_CMP_CREATE", "brand": "B", "product_name": "N",
         "status": "ACTIVE", "qa_verdict": "VALID", "identity_status": "VERIFIED"},
        actor_id="u1", roles={ROLE_EDITOR})
    assert p.status == "DRAFT"
    assert p.qa_verdict == "PENDING"
    assert p.identity_status == "NEEDS_REVIEW"


def test_product_create_schema_no_governance():
    f = set(ProductCreate.model_fields.keys())
    assert "status" not in f and "identity_status" not in f and "qa_verdict" not in f


def test_product_update_schema_no_governance():
    f = set(ProductUpdate.model_fields.keys())
    assert "status" not in f and "identity_status" not in f and "qa_verdict" not in f


def test_repository_rejects_status(db_session):
    _make_product(db_session, "P_CMP_REPO")
    with pytest.raises(ValidationError):
        ProductRepository(db_session).update("P_CMP_REPO", status="ACTIVE")


def test_service_rejects_governance(db_session):
    _make_product(db_session, "P_CMP_SVC")
    with pytest.raises(ValidationError):
        ProductService(db_session).update("P_CMP_SVC", qa_verdict="VALID")


def test_unauthenticated_patch_rejected(client, db_session):
    _make_product(db_session, "P_CMP_API1")
    assert client.patch("/api/v1/products/P_CMP_API1", json={"brand": "X"}).status_code in (401, 403)


def test_editor_can_edit_informational(client, db_session):
    _make_product(db_session, "P_CMP_API2")
    _seed_role(db_session, "ed1", ROLE_EDITOR, "UR_CMP1")
    r = client.patch("/api/v1/products/P_CMP_API2", json={"brand": "UpdatedBrand"},
                     headers=_auth_header("ed1"))
    assert r.status_code == 200
    assert r.json()["brand"] == "UpdatedBrand"
    assert r.json()["status"] == "DRAFT"


def test_editor_cannot_submit(db_session):
    _make_product(db_session, "P_CMP_SUB")
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).submit("P_CMP_SUB", "ed", {ROLE_EDITOR})


def test_lifecycle_submit_enter_qa(db_session):
    _make_product(db_session, "P_CMP_LIFE")
    tr = ProductTransitionService(db_session)
    assert tr.submit("P_CMP_LIFE", "rev", {ROLE_REVIEWER_QA}).status == "SUBMITTED"
    assert tr.enter_qa_review("P_CMP_LIFE", "rev", {ROLE_REVIEWER_QA}).status == "QA_REVIEW"


def test_invalid_transition_rejected(db_session):
    _make_product(db_session, "P_CMP_INV", status="DRAFT")
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).activate("P_CMP_INV", "po", {ROLE_PO})


def test_reject_requires_reason(db_session):
    _make_product(db_session, "P_CMP_REJ", status="QA_REVIEW")
    tr = ProductTransitionService(db_session)
    with pytest.raises(ValidationError):
        tr.reject("P_CMP_REJ", "rev", {ROLE_REVIEWER_QA}, "")
    assert tr.reject("P_CMP_REJ", "rev", {ROLE_REVIEWER_QA}, "bad quality").status == "REJECTED"


def test_mutation_log_persists(db_session):
    ProductService(db_session).create_product_with_inventory(
        {"product_id": "P_CMP_LOG", "brand": "B", "product_name": "N"},
        actor_id="u1", roles={ROLE_EDITOR})
    logs = MutationLogService(db_session).list_for_product("P_CMP_LOG")
    assert any(l.action == "CREATE" and l.actor_id == "u1" for l in logs)
    ProductTransitionService(db_session).submit("P_CMP_LOG", "rev", {ROLE_REVIEWER_QA})
    logs2 = MutationLogService(db_session).list_for_product("P_CMP_LOG")
    sub = next(l for l in logs2 if l.action == "SUBMIT")
    assert sub.before_state and sub.after_state and sub.resulting_state == "SUBMITTED"


def test_readiness_blocks_approve(db_session):
    _make_product(db_session, "P_CMP_RDY", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    assert EvidenceReadinessService(db_session).evaluate("P_CMP_RDY").ready is False
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY", "po", {ROLE_PO})


def test_readiness_pass_and_approve(db_session):
    _make_product(db_session, "P_CMP_RDY2", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_CMP_1", product_id="P_CMP_RDY2", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="VERIFIED", conflict_status="NONE"))
    db_session.flush()
    assert EvidenceReadinessService(db_session).evaluate("P_CMP_RDY2").ready is True
    assert ProductTransitionService(db_session).approve(
        "P_CMP_RDY2", "po", {ROLE_PO}).status == "APPROVED"


def test_active_grandfathered(db_session):
    assert _make_product(db_session, "P_CMP_LEGACY", status="ACTIVE").status == "ACTIVE"
