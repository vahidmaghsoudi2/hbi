from datetime import datetime, timezone


def _headers(customer_id):
    from app.core.auth import create_access_token
    token = create_access_token({"sub": customer_id})
    return {"Authorization": f"Bearer {token}"}


def _seed_case(db_session):
    from app.models.customer import Customer
    from app.models.case import Case
    customer = Customer(customer_id="OA-CUST-1", name="Outcome Owner", consent_to_store_data=1)
    db_session.add(customer)
    db_session.add(Customer(customer_id="OA-CUST-2", name="Outcome Other", consent_to_store_data=1))
    db_session.flush()
    case = Case(case_id="OA-CASE-1", customer_id=customer.customer_id, case_type="OPEN")
    foreign_case = Case(case_id="OA-CASE-2", customer_id="OA-CUST-2", case_type="OPEN")
    db_session.add_all([case, foreign_case])
    db_session.commit()
    return case.case_id, foreign_case.case_id


def _seed_recommendation(db_session, case_id, recommendation_id="OA-REC-1", product_id="OA-PROD-1"):
    from app.models.product import Product
    from app.models.recommendation import Recommendation
    db_session.add(Product(
        product_id=product_id,
        brand="HBI",
        product_name="Outcome Test Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    ))
    db_session.add(Recommendation(
        recommendation_id=recommendation_id,
        case_id=case_id,
        product_id=product_id,
        eligibility_status="ELIGIBLE",
        ranking_score=1.0,
    ))
    db_session.commit()
    return recommendation_id, product_id


def test_outcome_assessment_create_retrieve_and_audit(client, db_session, caplog):
    case_id, _ = _seed_case(db_session)
    recommendation_id, product_id = _seed_recommendation(db_session, case_id)
    response = client.post(
        "/api/v1/outcome-assessments",
        headers=_headers("OA-CUST-1"),
        json={
            "case_id": case_id,
            "recommendation_id": recommendation_id,
            "product_id": product_id,
            "result_state": "positive",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["result_state"] == "POSITIVE"
    assert body["provenance"] == "CUSTOMER"
    assert body["actor_id"] == "OA-CUST-1"
    assert body["recommendation_id"] == recommendation_id
    assert body["product_id"] == product_id

    listed = client.get(
        f"/api/v1/outcome-assessments/case/{case_id}",
        headers=_headers("OA-CUST-1"),
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["outcome_assessment_id"] == body["outcome_assessment_id"]


def test_outcome_assessment_unauthenticated_and_foreign_case(client, db_session):
    case_id, foreign_case_id = _seed_case(db_session)
    unauth = client.get(f"/api/v1/outcome-assessments/case/{case_id}")
    assert unauth.status_code == 401
    foreign = client.get(
        f"/api/v1/outcome-assessments/case/{foreign_case_id}",
        headers=_headers("OA-CUST-1"),
    )
    assert foreign.status_code == 403


def test_outcome_assessment_rejects_missing_and_cross_case_traces(client, db_session):
    case_id, foreign_case_id = _seed_case(db_session)
    rec_id, product_id = _seed_recommendation(db_session, foreign_case_id, "OA-REC-FOREIGN", "OA-PROD-FOREIGN")
    missing = client.post(
        "/api/v1/outcome-assessments",
        headers=_headers("OA-CUST-1"),
        json={"case_id": case_id, "recommendation_id": "NOPE", "result_state": "UNKNOWN"},
    )
    assert missing.status_code == 422
    foreign = client.post(
        "/api/v1/outcome-assessments",
        headers=_headers("OA-CUST-1"),
        json={"case_id": case_id, "recommendation_id": rec_id, "result_state": "UNKNOWN"},
    )
    assert foreign.status_code == 422


def test_outcome_assessment_requires_completed_followup(client, db_session):
    case_id, _ = _seed_case(db_session)
    rec_id, _ = _seed_recommendation(db_session, case_id)
    from app.models.follow_up import FollowUp
    db_session.add(FollowUp(
        follow_up_id="OA-FU-1",
        case_id=case_id,
        recommendation_id=rec_id,
        scheduled_at=datetime.now(timezone.utc),
        status="SCHEDULED",
        created_by="OA-CUST-1",
        updated_by="OA-CUST-1",
    ))
    db_session.commit()
    response = client.post(
        "/api/v1/outcome-assessments",
        headers=_headers("OA-CUST-1"),
        json={"case_id": case_id, "recommendation_id": rec_id, "follow_up_id": "OA-FU-1", "result_state": "PARTIAL"},
    )
    assert response.status_code == 422
    assert "COMPLETED" in response.text


def test_outcome_assessment_allows_completed_followup_and_multiple_records(client, db_session):
    case_id, _ = _seed_case(db_session)
    rec_id, product_id = _seed_recommendation(db_session, case_id)
    from app.models.follow_up import FollowUp
    db_session.add(FollowUp(
        follow_up_id="OA-FU-2",
        case_id=case_id,
        recommendation_id=rec_id,
        scheduled_at=datetime.now(timezone.utc),
        status="COMPLETED",
        created_by="OA-CUST-1",
        updated_by="OA-CUST-1",
    ))
    db_session.commit()
    for state in ["PARTIAL", "UNKNOWN"]:
        response = client.post(
            "/api/v1/outcome-assessments",
            headers=_headers("OA-CUST-1"),
            json={"case_id": case_id, "recommendation_id": rec_id, "follow_up_id": "OA-FU-2", "product_id": product_id, "result_state": state},
        )
        assert response.status_code == 201, response.text
    listed = client.get(
        f"/api/v1/outcome-assessments/case/{case_id}?recommendation_id={rec_id}",
        headers=_headers("OA-CUST-1"),
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 2
    assert {x["result_state"] for x in listed.json()} == {"PARTIAL", "UNKNOWN"}


def test_outcome_assessment_rejects_product_without_case_trace(client, db_session):
    case_id, _ = _seed_case(db_session)
    _seed_recommendation(db_session, case_id)
    from app.models.product import Product
    db_session.add(Product(
        product_id="OA-PROD-UNTRACED",
        brand="HBI",
        product_name="Untraced Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    ))
    db_session.commit()
    response = client.post(
        "/api/v1/outcome-assessments",
        headers=_headers("OA-CUST-1"),
        json={"case_id": case_id, "product_id": "OA-PROD-UNTRACED", "result_state": "NO_BENEFIT"},
    )
    assert response.status_code == 422
