from app.models.case import Case
from app.models.customer import Customer


def _create_customer_case(db, customer_id, case_id):
    db.add(Customer(
        customer_id=customer_id,
        name="Consultation API Test",
        consent_to_store_data=1,
    ))
    db.add(Case(
        case_id=case_id,
        customer_id=customer_id,
        case_type="SKIN",
    ))
    db.commit()


def _customer_token(client, customer_id):
    response = client.post(
        "/api/v1/auth/pilot-token",
        json={"customer_id": customer_id},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_consultation_output_api_is_customer_owned_and_read_only(client, db_session):
    _create_customer_case(db_session, "OUTPUT-CUSTOMER", "OUTPUT-CASE")
    token = _customer_token(client, "OUTPUT-CUSTOMER")

    response = client.get(
        "/api/v1/recommendations/case/OUTPUT-CASE/consultation-output",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"] == "OUTPUT-CASE"
    assert body["consultation_context_status"] == "NOT_RECORDED"
    assert body["recommendation_status"] == "NO_ELIGIBLE_RECOMMENDATION"
    assert body["recommendation_count"] == 0
    assert body["computed_only"] is True


def test_explainable_suitability_api_rejects_p22_and_enforces_case_ownership(client, db_session):
    _create_customer_case(db_session, "SUITABILITY-CUSTOMER", "SUITABILITY-CASE")
    token = _customer_token(client, "SUITABILITY-CUSTOMER")

    invalid_problem = client.get(
        "/api/v1/recommendations/case/SUITABILITY-CASE/suitability/P22",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert invalid_problem.status_code == 422

    _create_customer_case(
        db_session, "OTHER-SUITABILITY-CUSTOMER", "OTHER-SUITABILITY-CASE"
    )
    denied = client.get(
        "/api/v1/recommendations/case/OTHER-SUITABILITY-CASE/suitability/P17",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert denied.status_code == 403
