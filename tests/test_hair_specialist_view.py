from dataclasses import replace

import pytest

from app.domain.hair_catalog_identity_lookup import CatalogIdentity
from app.domain.hair_data_governance import (
    HAIR_DATA_GOVERNANCE_POLICY,
    HAIR_ROLE_CAPABILITIES,
    is_permitted_synthetic_case,
)
from app.domain.hair_knowledge_case_bridge import (
    HairCaseSnapshot,
    HairKnowledgeCaseBridge,
    build_approved_catalog_knowledge_package,
    build_catalog_identity_rule,
)
from app.domain.hair_specialist_view import build_hair_specialist_view


def _run(**case_changes):
    package = build_approved_catalog_knowledge_package()
    assert package is not None
    rule = build_catalog_identity_rule(package)
    case_values = {
        "case_id": "SYNTHETIC-ROW69-001",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "service_kind": "CATALOG_READY",
        "catalog_identity": CatalogIdentity(
            brand="بیجورکا",
            series="طبیعی",
            shade_number="۱",
            shade_name="مشکی",
        ),
        "synthetic_data": True,
    }
    case_values.update(case_changes)
    case = HairCaseSnapshot(**case_values)
    return HairKnowledgeCaseBridge().run(
        case=case,
        package=package,
        rule=rule,
        run_id="SYNTHETIC-ROW69-RUN-001",
    )


def test_po_66_09_is_explicitly_synthetic_only_and_non_persistent():
    policy = HAIR_DATA_GOVERNANCE_POLICY
    assert policy.policy_id == "PO-66-09"
    assert policy.data_class == "SYNTHETIC_ONLY"
    assert policy.real_client_data_enabled is False
    assert policy.persistence_enabled is False
    assert policy.real_client_retention_seconds == 0
    assert policy.exceptions == ()
    assert policy.jurisdiction_status == "UNAPPROVED_PRODUCTION_BLOCKED"


def test_only_synthetic_case_ids_and_flag_are_permitted():
    assert is_permitted_synthetic_case(
        case_id="SYNTHETIC-001", synthetic_data=True
    )
    assert not is_permitted_synthetic_case(
        case_id="CASE-001", synthetic_data=True
    )
    assert not is_permitted_synthetic_case(
        case_id="SYNTHETIC-001", synthetic_data=False
    )


def test_role_matrix_is_least_privilege_and_admin_does_not_approve_domain_rules():
    assert "READ_SYNTHETIC_SPECIALIST_VIEW" not in HAIR_ROLE_CAPABILITIES["Editor"]
    assert "READ_SYNTHETIC_SPECIALIST_VIEW" in HAIR_ROLE_CAPABILITIES["Reviewer/QA"]
    assert "APPROVE_PRODUCT_SCOPE" in HAIR_ROLE_CAPABILITIES["PO"]
    assert "APPROVE_PRODUCT_SCOPE" not in HAIR_ROLE_CAPABILITIES["Admin"]


def test_success_view_is_internal_synthetic_and_never_a_recommendation():
    view = build_hair_specialist_view(_run())
    assert view["audience"] == "INTERNAL_REVIEW_ONLY"
    assert view["data_class"] == "SYNTHETIC_ONLY"
    assert view["decision"]["recommendation"] is None
    assert view["decision"]["display_allowed"] is False
    assert view["decision"]["client_visible"] is False
    assert view["lineage"]["persistence"] == "COMPUTED_ONLY"
    assert view["limitations"]
    assert view["review_controls"]["available_actions"] == []


def test_view_exposes_evidence_and_complete_lineage_without_raw_engine_result():
    view = build_hair_specialist_view(_run())
    assert view["evidence"]
    assert view["lineage"]["snapshot_id"]
    assert view["lineage"]["content_sha256"]
    assert view["lineage"]["dependencies"]
    assert "reasoning_result" not in view
    assert "product_id" not in view


def test_view_never_inherits_acceptance_consent_or_specialist_review():
    view = build_hair_specialist_view(_run())
    controls = view["review_controls"]
    assert controls["acceptance_inherited"] is False
    assert controls["execution_consent_inherited"] is False
    assert controls["specialist_review_recorded"] is False


def test_non_synthetic_run_is_rejected_by_view_contract():
    run = _run()
    non_synthetic = replace(run, case_id="CASE-REAL-001")
    with pytest.raises(ValueError):
        build_hair_specialist_view(non_synthetic)


def test_blocked_run_has_safe_status_and_no_recommendation():
    run = _run(service_kind="COMBINATION_CONSULT")
    view = build_hair_specialist_view(run)
    assert view["decision"]["status"] == "STOP_OUT_OF_DOMAIN"
    assert view["decision"]["recommendation"] is None
    assert view["decision"]["display_allowed"] is False


def test_unmapped_status_fails_closed_in_presentation():
    run = _run()
    unknown = replace(run, status="UNRECOGNIZED_STATUS")
    view = build_hair_specialist_view(unknown)
    assert "منتشر نمی‌شود" in view["decision"]["summary_fa"]
    assert view["decision"]["display_allowed"] is False


# API boundary tests for the specialist-only preview route.
from app.core.auth import create_access_token
from app.models.user_role import ROLE_REVIEWER_QA, UserRole


def _headers():
    token = create_access_token({"sub": "hair-row69-test-user"})
    return {"Authorization": f"Bearer {token}"}


def _grant_reviewer_qa(db_session):
    db_session.add(
        UserRole(
            user_role_id="HAIR-ROW69-REVIEWER",
            subject_id="hair-row69-test-user",
            role=ROLE_REVIEWER_QA,
        )
    )
    db_session.commit()


def _preview_payload(**overrides):
    payload = {
        "case_id": "SYNTHETIC-ROW69-API-001",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "service_kind": "CATALOG_READY",
        "catalog_identity": {
            "brand": "بیجورکا",
            "series": "طبیعی",
            "shade_number": "۱",
            "shade_name": "مشکی",
        },
    }
    payload.update(overrides)
    return payload


def test_specialist_preview_requires_internal_role(client, db_session):
    response = client.post(
        "/api/v1/hair/specialist-preview",
        json=_preview_payload(),
        headers=_headers(),
    )
    assert response.status_code == 403


def test_specialist_preview_rejects_non_synthetic_case_id(client, db_session):
    _grant_reviewer_qa(db_session)
    response = client.post(
        "/api/v1/hair/specialist-preview",
        json=_preview_payload(case_id="CASE-REAL-001"),
        headers=_headers(),
    )
    assert response.status_code == 422


def test_specialist_preview_returns_internal_evidence_and_limits_only(client, db_session):
    _grant_reviewer_qa(db_session)
    response = client.post(
        "/api/v1/hair/specialist-preview",
        json=_preview_payload(),
        headers=_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["audience"] == "INTERNAL_REVIEW_ONLY"
    assert body["data_class"] == "SYNTHETIC_ONLY"
    assert body["decision"]["recommendation"] is None
    assert body["decision"]["display_allowed"] is False
    assert body["decision"]["client_visible"] is False
    assert body["evidence"]
    assert body["lineage"]["persistence"] == "COMPUTED_ONLY"
    assert body["limitations"]


def test_specialist_preview_rejects_client_controlled_policy_fields(client, db_session):
    _grant_reviewer_qa(db_session)
    payload = _preview_payload()
    payload["synthetic_data"] = False
    response = client.post(
        "/api/v1/hair/specialist-preview",
        json=payload,
        headers=_headers(),
    )
    assert response.status_code == 422


def test_specialist_preview_fails_closed_for_out_of_scope_service(client, db_session):
    _grant_reviewer_qa(db_session)
    response = client.post(
        "/api/v1/hair/specialist-preview",
        json=_preview_payload(service_kind="COMBINATION_CONSULT"),
        headers=_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["status"] == "STOP_OUT_OF_DOMAIN"
    assert body["decision"]["recommendation"] is None
    assert body["decision"]["display_allowed"] is False
