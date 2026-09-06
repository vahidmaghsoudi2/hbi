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


# ─── WP-03: Evidence Readiness branch coverage (Issue #17) ───

def test_readiness_conflict_blocks_approve(db_session):
    """GAP-1: VERIFIED + CONFLICT must block readiness and approve."""
    _make_product(db_session, "P_CMP_RDY_CF", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_CF_1", product_id="P_CMP_RDY_CF", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="VERIFIED", conflict_status="CONFLICT"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_CF")
    assert result.ready is False
    assert "E_CF_1" in result.blocking_conflicts
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY_CF", "po", {ROLE_PO})


def test_readiness_rejected_evidence_blocks_approve(db_session):
    """GAP-2: REJECTED evidence must appear in unacceptable and block approve."""
    _make_product(db_session, "P_CMP_RDY_RJ", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_RJ_1", product_id="P_CMP_RDY_RJ", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="REJECTED", conflict_status="NONE"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_RJ")
    assert result.ready is False
    assert "E_RJ_1" in result.unacceptable_evidence_ids
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY_RJ", "po", {ROLE_PO})


def test_readiness_pending_qa_blocks_approve(db_session):
    """GAP-3: PENDING QA must appear in incomplete_qa and block approve."""
    _make_product(db_session, "P_CMP_RDY_PN", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_PN_1", product_id="P_CMP_RDY_PN", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="PENDING", conflict_status="NONE"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_PN")
    assert result.ready is False
    assert "E_PN_1" in result.incomplete_qa_evidence_ids
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY_PN", "po", {ROLE_PO})


def test_readiness_needs_review_blocks_approve(db_session):
    """GAP-4: NEEDS_REVIEW QA must appear in incomplete_qa and block approve."""
    _make_product(db_session, "P_CMP_RDY_NR", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_NR_1", product_id="P_CMP_RDY_NR", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="NEEDS_REVIEW", conflict_status="NONE"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_NR")
    assert result.ready is False
    assert "E_NR_1" in result.incomplete_qa_evidence_ids
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY_NR", "po", {ROLE_PO})


def test_readiness_approved_evidence_passes(db_session):
    """GAP-5: qa_status=APPROVED is an acceptable QA state (not only VERIFIED)."""
    _make_product(db_session, "P_CMP_RDY_AP", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_AP_1", product_id="P_CMP_RDY_AP", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="APPROVED", conflict_status="NONE"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_AP")
    assert result.ready is True
    assert result.missing_required == []
    assert ProductTransitionService(db_session).approve(
        "P_CMP_RDY_AP", "po", {ROLE_PO}).status == "APPROVED"


def test_readiness_acceptable_plus_incomplete_still_blocks(db_session):
    """GAP-6: one acceptable evidence does not override incomplete QA on another."""
    _make_product(db_session, "P_CMP_RDY_MX", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    db_session.add(Evidence(
        evidence_id="E_MX_OK", product_id="P_CMP_RDY_MX", source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="VERIFIED", conflict_status="NONE"))
    db_session.add(Evidence(
        evidence_id="E_MX_PEND", product_id="P_CMP_RDY_MX", source_type="PEER_REVIEWED",
        source_reference="s2", claim="c2", qa_status="PENDING", conflict_status="NONE"))
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate("P_CMP_RDY_MX")
    assert result.ready is False
    assert "E_MX_PEND" in result.incomplete_qa_evidence_ids
    assert result.missing_required == []  # acceptable_count > 0
    with pytest.raises(ValidationError):
        ProductTransitionService(db_session).approve("P_CMP_RDY_MX", "po", {ROLE_PO})


# ─── WP-02: Generic PATCH governance rejection (Issue #16) ───

def test_patch_rejects_status_only(client, db_session):
    """WP-02: governance field alone must be rejected at schema boundary (422)."""
    _make_product(db_session, "P_CMP_WP02_A")
    _seed_role(db_session, "ed_wp02", ROLE_EDITOR, "UR_WP02_A")
    r = client.patch(
        "/api/v1/products/P_CMP_WP02_A",
        json={"status": "APPROVED"},
        headers=_auth_header("ed_wp02"),
    )
    assert r.status_code == 422
    body = r.json()
    assert "status" in str(body).lower() or "extra" in str(body).lower() or "forbidden" in str(body).lower()


def test_patch_rejects_identity_status(client, db_session):
    """WP-02: identity_status via generic PATCH must be rejected."""
    _make_product(db_session, "P_CMP_WP02_B")
    _seed_role(db_session, "ed_wp02b", ROLE_EDITOR, "UR_WP02_B")
    r = client.patch(
        "/api/v1/products/P_CMP_WP02_B",
        json={"identity_status": "VERIFIED"},
        headers=_auth_header("ed_wp02b"),
    )
    assert r.status_code == 422


def test_patch_rejects_qa_verdict(client, db_session):
    """WP-02: qa_verdict via generic PATCH must be rejected."""
    _make_product(db_session, "P_CMP_WP02_C")
    _seed_role(db_session, "ed_wp02c", ROLE_EDITOR, "UR_WP02_C")
    r = client.patch(
        "/api/v1/products/P_CMP_WP02_C",
        json={"qa_verdict": "VALID"},
        headers=_auth_header("ed_wp02c"),
    )
    assert r.status_code == 422


def test_patch_rejects_mixed_governance(client, db_session):
    """WP-02: informational + governance in same PATCH must reject entire payload."""
    _make_product(db_session, "P_CMP_WP02_D", brand="Original")
    _seed_role(db_session, "ed_wp02d", ROLE_EDITOR, "UR_WP02_D")
    r = client.patch(
        "/api/v1/products/P_CMP_WP02_D",
        json={"brand": "Legitimate Update", "status": "APPROVED"},
        headers=_auth_header("ed_wp02d"),
    )
    assert r.status_code == 422
    p = ProductService(db_session).get_by_id("P_CMP_WP02_D")
    assert p.brand == "Original"
    assert p.status == "DRAFT"


# ─── WP-04: Mutation log for remaining lifecycle actions (Issue #18) ───
# Existing: test_mutation_log_persists covers CREATE + SUBMIT only.


def _logs_by_action(db, product_id, action):
    return [l for l in MutationLogService(db).list_for_product(product_id) if l.action == action]


def _seed_ready_evidence(db, product_id, eid="E_WP04"):
    db.add(Evidence(
        evidence_id=eid, product_id=product_id, source_type="PEER_REVIEWED",
        source_reference="s1", claim="c1", qa_status="VERIFIED", conflict_status="NONE"))
    db.flush()


def test_mutation_log_qa_change(db_session):
    """WP-04: QA_CHANGE must persist before/after and actor."""
    _make_product(db_session, "P_ML_QA", status="QA_REVIEW")
    ProductTransitionService(db_session).set_product_qa(
        "P_ML_QA", "rev_ml", {ROLE_REVIEWER_QA}, "VALID", notes="ok")
    rows = _logs_by_action(db_session, "P_ML_QA", "QA_CHANGE")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "rev_ml"
    assert row.actor_role == ROLE_REVIEWER_QA
    assert row.before_state and "PENDING" in row.before_state
    assert row.after_state and "VALID" in row.after_state
    assert row.resulting_state == "QA_REVIEW"


def test_mutation_log_identity_change(db_session):
    """WP-04: IDENTITY_CHANGE must persist before/after."""
    _make_product(db_session, "P_ML_ID", status="QA_REVIEW", identity_status="NEEDS_REVIEW")
    ProductTransitionService(db_session).verify_identity(
        "P_ML_ID", "rev_ml", {ROLE_REVIEWER_QA}, "VERIFIED", source_refs="ref1", confidence=0.9)
    rows = _logs_by_action(db_session, "P_ML_ID", "IDENTITY_CHANGE")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "rev_ml"
    assert "NEEDS_REVIEW" in (row.before_state or "")
    assert "VERIFIED" in (row.after_state or "")
    assert row.resulting_state == "QA_REVIEW"


def test_mutation_log_approve(db_session):
    """WP-04: APPROVE must log status transition QA_REVIEW → APPROVED."""
    _make_product(db_session, "P_ML_AP", status="QA_REVIEW",
                  qa_verdict="VALID", identity_status="VERIFIED")
    _seed_ready_evidence(db_session, "P_ML_AP", "E_ML_AP")
    ProductTransitionService(db_session).approve("P_ML_AP", "po_ml", {ROLE_PO})
    rows = _logs_by_action(db_session, "P_ML_AP", "APPROVE")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "po_ml"
    assert row.actor_role == ROLE_PO
    assert row.resulting_state == "APPROVED"
    assert "QA_REVIEW" in (row.before_state or "")
    assert "APPROVED" in (row.after_state or "")


def test_mutation_log_activate(db_session):
    """WP-04: ACTIVATE must log APPROVED → ACTIVE."""
    _make_product(db_session, "P_ML_AC", status="APPROVED",
                  qa_verdict="VALID", identity_status="VERIFIED")
    _seed_ready_evidence(db_session, "P_ML_AC", "E_ML_AC")
    ProductTransitionService(db_session).activate("P_ML_AC", "po_ml", {ROLE_PO})
    rows = _logs_by_action(db_session, "P_ML_AC", "ACTIVATE")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "po_ml"
    assert row.resulting_state == "ACTIVE"
    assert "APPROVED" in (row.before_state or "")
    assert "ACTIVE" in (row.after_state or "")


def test_mutation_log_reject_with_reason(db_session):
    """WP-04: REJECT must log reason and resulting REJECTED."""
    _make_product(db_session, "P_ML_RJ", status="QA_REVIEW")
    ProductTransitionService(db_session).reject(
        "P_ML_RJ", "rev_ml", {ROLE_REVIEWER_QA}, "quality failure")
    rows = _logs_by_action(db_session, "P_ML_RJ", "REJECT")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "rev_ml"
    assert row.reason == "quality failure"
    assert row.resulting_state == "REJECTED"
    assert "QA_REVIEW" in (row.before_state or "")
    assert "REJECTED" in (row.after_state or "")


def test_mutation_log_archive(db_session):
    """WP-04: ARCHIVE must log ACTIVE → ARCHIVED."""
    _make_product(db_session, "P_ML_AR", status="ACTIVE",
                  qa_verdict="VALID", identity_status="VERIFIED")
    ProductTransitionService(db_session).archive(
        "P_ML_AR", "po_ml", {ROLE_PO}, reason="end of life")
    rows = _logs_by_action(db_session, "P_ML_AR", "ARCHIVE")
    assert len(rows) == 1
    row = rows[0]
    assert row.actor_id == "po_ml"
    assert row.actor_role == ROLE_PO
    assert row.reason == "end of life"
    assert row.resulting_state == "ARCHIVED"
    assert "ACTIVE" in (row.before_state or "")
    assert "ARCHIVED" in (row.after_state or "")
