from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.api.routers.hair_catalog import get_approved_hair_catalog_reference
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


def _payload(**overrides):
    payload = {
        "service_kind": "CATALOG_READY",
        "expected": {
            "brand": "Bijourka",
            "series": "Natural",
            "shade_number": "1",
            "shade_name": "Black",
            "size_value": "100",
            "size_unit": "ml",
        },
        "observed": {
            "brand": "Bijourka",
            "series": "Natural",
            "shade_number": "1",
            "shade_name": "Black",
            "size_value": "100",
            "size_unit": "ml",
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

    def test_missing_primary_catalog_reference_fails_closed(self, client, db_session):
        _grant_po(db_session)
        response = client.post(
            "/api/v1/hair/catalog-identity/lookup",
            json=_payload(),
            headers=_headers(),
        )
        assert response.status_code == 200
        body = response.json()
        assert body == {
            "status": "KNOWLEDGE_GAP",
            "display_allowed": False,
            "message": "مرجع اصلیِ مصوب و نسخه‌دار کاتالوگ هنوز در سامانه ثبت نشده است؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        }

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
        synthetic_reference = CatalogReference(
            source_kind="RAEAKA_BIJOURKA_CATALOG",
            approval_status="PO_APPROVED",
            url="https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/",
            edition_label="SYNTHETIC-TEST-EDITION",
            captured_at="2026-11-09T12:00:00+00:00",
            content_sha256="a" * 64,
        )
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
