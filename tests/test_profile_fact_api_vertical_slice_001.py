"""API Vertical Slice 001 for the explicit ProfileFact durable write boundary."""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.product_mutation_log import ProductMutationLog
from app.models.profile_fact import ProfileFact
from app.services.customer_service import CustomerService


def _auth(customer_id: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': customer_id})}"}


def _customer(db_session, *, consent: int = 1, name: str = "ProfileFact API") :
    return CustomerService(db_session).register_guest(
        name=name,
        consent_to_store_data=consent,
    )


def test_create_profile_fact_persists_and_audits(client, db_session):
    customer = _customer(db_session)

    response = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={
            "attribute_key": "skin_profile",
            "value": "حساس",
            "value_state": "KNOWN",
            "provenance": "CUSTOMER",
            "reason": "customer-confirmed",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["customer_id"] == customer.customer_id
    assert body["attribute_key"] == "skin_profile"
    assert body["status"] == "ACTIVE"

    db_session.expire_all()
    logs = (
        db_session.query(ProductMutationLog)
        .filter(
            ProductMutationLog.target_entity == "ProfileFact",
            ProductMutationLog.target_id == body["profile_fact_id"],
        )
        .all()
    )
    assert len(logs) == 1
    assert logs[0].action == "CREATE"
    assert logs[0].actor_id == customer.customer_id


def test_profile_fact_write_requires_auth(client):
    response = client.post(
        "/api/v1/customers/profile-facts",
        json={"attribute_key": "skin_profile", "value": "حساس"},
    )
    assert response.status_code == 401


def test_profile_fact_foreign_fact_is_forbidden(client, db_session):
    owner = _customer(db_session, name="Owner")
    other = _customer(db_session, name="Other")

    created = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(owner.customer_id),
        json={"attribute_key": "skin_profile", "value": "خشک"},
    )
    assert created.status_code == 201
    fact_id = created.json()["profile_fact_id"]

    response = client.post(
        f"/api/v1/customers/profile-facts/{fact_id}/supersede",
        headers=_auth(other.customer_id),
        json={"value": "چرب"},
    )
    assert response.status_code == 403


def test_profile_fact_create_requires_consent(client, db_session):
    customer = _customer(db_session, consent=0)

    response = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "skin_profile", "value": "خشک"},
    )

    assert response.status_code == 422
    assert "consent" in response.json()["detail"].lower()


def test_profile_fact_invalid_input_returns_422(client, db_session):
    customer = _customer(db_session)

    invalid_key = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "favorite_color", "value": "red"},
    )
    assert invalid_key.status_code == 422

    empty_known = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "skin_profile", "value": " "},
    )
    assert empty_known.status_code == 422


def test_profile_fact_supersede_versions_and_audits(client, db_session):
    customer = _customer(db_session)

    first = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "age_range", "value": "25-34"},
    )
    assert first.status_code == 201
    first_id = first.json()["profile_fact_id"]

    replacement = client.post(
        f"/api/v1/customers/profile-facts/{first_id}/supersede",
        headers=_auth(customer.customer_id),
        json={
            "value": "35-44",
            "value_state": "KNOWN",
            "provenance": "CUSTOMER",
            "reason": "customer-updated",
        },
    )

    assert replacement.status_code == 200, replacement.text
    replacement_body = replacement.json()
    assert replacement_body["status"] == "ACTIVE"
    assert replacement_body["supersedes_fact_id"] == first_id

    db_session.expire_all()
    first_row = db_session.get(ProfileFact, first_id)
    assert first_row.status == "SUPERSEDED"
    logs = (
        db_session.query(ProductMutationLog)
        .filter(
            ProductMutationLog.target_entity == "ProfileFact",
            ProductMutationLog.target_id == replacement_body["profile_fact_id"],
        )
        .all()
    )
    assert len(logs) == 1
    assert logs[0].action == "SUPERSEDE"


def test_profile_fact_revoke_is_lifecycle_action_and_audited(client, db_session):
    customer = _customer(db_session)

    created = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "concerns", "value": "لک"},
    )
    fact_id = created.json()["profile_fact_id"]

    response = client.post(
        f"/api/v1/customers/profile-facts/{fact_id}/revoke",
        headers=_auth(customer.customer_id),
        json={"reason": "customer-withdrew"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "REVOKED"

    db_session.expire_all()
    logs = (
        db_session.query(ProductMutationLog)
        .filter(
            ProductMutationLog.target_entity == "ProfileFact",
            ProductMutationLog.target_id == fact_id,
            ProductMutationLog.action == "REVOKE",
        )
        .all()
    )
    assert len(logs) == 1


def test_profile_fact_list_active_filters_lifecycle_states(client, db_session):
    customer = _customer(db_session)

    active = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "skin_profile", "value": "خشک"},
    ).json()

    revoked = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "concerns", "value": "لک"},
    ).json()

    superseded = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "age_range", "value": "25-34"},
    ).json()

    assert client.post(
        f"/api/v1/customers/profile-facts/{revoked['profile_fact_id']}/revoke",
        headers=_auth(customer.customer_id),
        json={},
    ).status_code == 200

    assert client.post(
        f"/api/v1/customers/profile-facts/{superseded['profile_fact_id']}/supersede",
        headers=_auth(customer.customer_id),
        json={"value": "35-44"},
    ).status_code == 200

    response = client.get(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
    )
    assert response.status_code == 200
    ids = {item["profile_fact_id"] for item in response.json()}
    assert active["profile_fact_id"] in ids
    assert revoked["profile_fact_id"] not in ids
    assert superseded["profile_fact_id"] not in ids


def test_profile_fact_list_requires_consent(client, db_session):
    customer = _customer(db_session)
    created = client.post(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
        json={"attribute_key": "skin_profile", "value": "خشک"},
    )
    assert created.status_code == 201

    customer.consent_to_store_data = 0
    db_session.commit()

    response = client.get(
        "/api/v1/customers/profile-facts",
        headers=_auth(customer.customer_id),
    )
    assert response.status_code == 422


def test_missing_profile_fact_returns_404(client, db_session):
    customer = _customer(db_session)
    response = client.post(
        "/api/v1/customers/profile-facts/PF-missing/revoke",
        headers=_auth(customer.customer_id),
        json={},
    )
    assert response.status_code == 404
