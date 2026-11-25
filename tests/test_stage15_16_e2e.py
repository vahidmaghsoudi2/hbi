"""Stage 15-16 end-to-end contract across customer, Case, consultation and output APIs.

All records are created only in the shared in-memory pytest database.
"""
from app.models.case import Case
from app.models.customer import Customer


def _pilot_token(client, customer_id):
    response = client.post(
        "/api/v1/auth/pilot-token",
        json={"customer_id": customer_id},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_customer_consultation_to_explainable_output_e2e(client, db_session):
    customer_id = "STAGE15-CUSTOMER"
    db_session.add(Customer(
        customer_id=customer_id,
        name="Stage 15 E2E Customer",
        consent_to_store_data=1,
    ))
    db_session.commit()
    token = _pilot_token(client, customer_id)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": customer_id, "case_type": "SKIN"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["case_id"]

    context = {
        "affected_areas": ["cheek", "forehead"],
        "duration": "two weeks",
        "severity": 5,
        "aggravating_factors": ["sun exposure"],
        "current_products": ["cleanser"],
        "notes": "Stage 15 disposable E2E fixture",
    }
    saved = client.put(
        f"/api/v1/cases/{case_id}/consultation",
        headers=headers,
        json=context,
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["consultation_context"] == context

    restored = client.get(
        f"/api/v1/cases/{case_id}/consultation",
        headers=headers,
    )
    assert restored.status_code == 200, restored.text
    assert restored.json()["consultation_context"] == context

    output = client.get(
        f"/api/v1/recommendations/case/{case_id}/consultation-output",
        headers=headers,
    )
    assert output.status_code == 200, output.text
    body = output.json()
    assert body["consultation_context_status"] == "PRESENT"
    assert body["consultation_context"] == context
    assert body["recommendation_status"] == "NO_ELIGIBLE_RECOMMENDATION"
    assert body["recommendation_count"] == 0
    assert body["recommendations"] == []
    assert body["computed_only"] is True

    suitability = client.get(
        f"/api/v1/recommendations/case/{case_id}/suitability/P17",
        headers=headers,
    )
    assert suitability.status_code == 200, suitability.text
    suitability_body = suitability.json()
    assert suitability_body["problem_id"] == "P17"
    assert suitability_body["candidate_count"] == 0
    assert suitability_body["recommendation_eligible"] is False
    assert suitability_body["candidates"] == []

    context_only = client.get(
        f"/api/v1/recommendations/case/{case_id}/suitability/P22",
        headers=headers,
    )
    assert context_only.status_code == 422

    foreign_customer_id = "STAGE15-FOREIGN-CUSTOMER"
    db_session.add(Customer(
        customer_id=foreign_customer_id,
        name="Foreign Stage 15 Customer",
        consent_to_store_data=1,
    ))
    db_session.commit()
    foreign_token = _pilot_token(client, foreign_customer_id)
    foreign_case = client.post(
        "/api/v1/cases/",
        headers={"Authorization": f"Bearer {foreign_token}"},
        json={"customer_id": foreign_customer_id, "case_type": "SKIN"},
    )
    assert foreign_case.status_code == 201, foreign_case.text
    denied = client.get(
        f"/api/v1/recommendations/case/{foreign_case.json()['case_id']}/consultation-output",
        headers=headers,
    )
    assert denied.status_code == 403
