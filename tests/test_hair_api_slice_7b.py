from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.api.routers.hair_catalog import get_approved_hair_catalog_reference
from app.domain.hair_catalog_provider import load_approved_hair_catalog_reference
from app.domain.hair_catalog_identity_lookup import CatalogReference
from app.models.user_role import ROLE_PO, UserRole


def _headers():
    token = create_access_token({"sub": "hair-api-test-user"})
    return {"Authorization": f"Bearer {token}"}


def _grant_po(db_session):
    db_session.add(
        UserRole(
            user_role_id="HAIR-API-TEST-PO",
            subject_id="hair-api-test-user",
            role=ROLE_PO,
        )
    )
    db_session.commit()


def _synthetic_reference():
    loaded = load_approved_hair_catalog_reference()
    assert loaded is not None
    _, approved_reference = loaded
    return CatalogReference(
        source_kind="RAEAKA_BIJOURKA_CATALOG",
        approval_status="PO_APPROVED",
        url="https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/",
        edition_label="SYNTHETIC-TEST-EDITION",
        captured_at="2026-11-09T12:00:00+00:00",
        content_sha256=approved_reference.content_sha256,
    )


def _payload(**overrides):
    payload = {
        "service_kind": "CATALOG_READY",
        "expected": {
            "brand": "بیجورکا",
            "series": "طبیعی",
            "shade_number": "۱",
            "shade_name": "مشکی",
            "product_specification": "Synthetic product details",
            "product_volume": "100 ml",
        },
        "observed": {
            "brand": "بیجورکا",
            "series": "طبیعی",
            "shade_number": "۱",
            "shade_name": "مشکی",
            "product_specification": "Synthetic product details",
            "product_volume": "100 ml",
        },
    }
    payload.update(overrides)
    return payload


class TestHairCatalogApiSlice7B:
    def test_endpoint_requires_server_side_role(self, client, db_session):
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=_payload(),
            headers=_headers(),
        )
        assert response.status_code == 403

    def test_server_csv_reference_is_loaded_but_unversioned_lookup_fails_closed(
        self, client, db_session
    ):
        _grant_po(db_session)
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=_payload(),
            headers=_headers(),
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "WITHHOLD_INCONCLUSIVE"
        assert body["display_allowed"] is False
        assert "نسخه‌دار و قابل‌ردیابی" in body["message"]

    def test_unapproved_expected_identity_is_not_accepted_as_catalog_baseline(
        self, client, db_session
    ):
        _grant_po(db_session)
        payload = _payload()
        payload["expected"]["shade_number"] = "NOT-IN-APPROVED-CATALOG"
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=payload,
            headers=_headers(),
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "WITHHOLD_INCONCLUSIVE"
        assert body["display_allowed"] is False
        assert "کاتالوگ مصوب سمت سرور" in body["message"]

    def test_caller_cannot_supply_or_override_reference_approval_metadata(
        self, client, db_session
    ):
        _grant_po(db_session)
        payload = _payload()
        payload["reference"] = {
            "source_kind": "RAEAKA_BIJOURKA_CATALOG",
            "approval_status": "PO_APPROVED",
            "edition_label": "claimed-edition",
            "captured_at": "2026-11-09T12:00:00+00:00",
            "content_sha256": "a" * 64,
            "url": "https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/",
        }
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=payload,
            headers=_headers(),
        )
        assert response.status_code == 422

    def test_out_of_scope_service_is_stopped(self, client, db_session):
        _grant_po(db_session)
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=_payload(service_kind="COMBINATION_CONSULT"),
            headers=_headers(),
        )
        assert response.status_code == 200
        assert response.json()["status"] == "OUT_OF_DOMAIN"
        assert response.json()["display_allowed"] is False

    def test_server_owned_synthetic_reference_can_reach_display_gate(
        self, client, db_session
    ):
        _grant_po(db_session)
        synthetic_reference = _synthetic_reference()
        app.dependency_overrides[get_approved_hair_catalog_reference] = (
            lambda: ("SYNTHETIC-ONLY-REFERENCE", synthetic_reference)
        )
        try:
            response = client.post(
                "/api/v1/hair/catalog-identity/lookup",
                json=_payload(),
                headers=_headers(),
            )
        finally:
            app.dependency_overrides.pop(
                get_approved_hair_catalog_reference, None
            )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "IDENTITY_MATCH_DISPLAYABLE"
        assert body["display_allowed"] is True
        assert "ایمنی" in body["message"]
        assert "chemical" not in body
        assert "source_url" not in body
        assert "decision_output_id" not in body

    def test_product_volume_and_specification_do_not_affect_identity_match(
        self, client, db_session
    ):
        _grant_po(db_session)
        synthetic_reference = _synthetic_reference()
        app.dependency_overrides[get_approved_hair_catalog_reference] = (
            lambda: ("SYNTHETIC-ONLY-REFERENCE", synthetic_reference)
        )
        payload = _payload()
        payload["expected"]["product_specification"] = "Details A"
        payload["expected"]["product_volume"] = "50 ml"
        payload["observed"]["product_specification"] = "Details B"
        payload["observed"]["product_volume"] = "100 ml"
        try:
            response = client.post(
                "/api/v1/hair/catalog-identity/lookup",
                json=payload,
                headers=_headers(),
            )
        finally:
            app.dependency_overrides.pop(
                get_approved_hair_catalog_reference, None
            )

        assert response.status_code == 200
        assert response.json()["status"] == "IDENTITY_MATCH_DISPLAYABLE"

    def test_product_details_are_optional_for_identity_lookup(
        self, client, db_session
    ):
        _grant_po(db_session)
        synthetic_reference = _synthetic_reference()
        app.dependency_overrides[get_approved_hair_catalog_reference] = (
            lambda: ("SYNTHETIC-ONLY-REFERENCE", synthetic_reference)
        )
        payload = _payload()
        for side in ("expected", "observed"):
            payload[side].pop("product_specification")
            payload[side].pop("product_volume")
        try:
            response = client.post(
                "/api/v1/hair/catalog-identity/lookup",
                json=payload,
                headers=_headers(),
            )
        finally:
            app.dependency_overrides.pop(
                get_approved_hair_catalog_reference, None
            )

        assert response.status_code == 200
        assert response.json()["status"] == "IDENTITY_MATCH_DISPLAYABLE"

