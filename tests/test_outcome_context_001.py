from datetime import datetime, timedelta, timezone
from unittest.mock import patch


def _headers(customer_id):
    from app.core.auth import create_access_token
    token = create_access_token({"sub": customer_id})
    return {"Authorization": f"Bearer {token}"}


def _seed_customer_case(db_session):
    from app.models.customer import Customer
    from app.models.case import Case

    customer = Customer(
        customer_id="OCTX-CUST-1",
        name="Outcome Context Owner",
        consent_to_store_data=1,
    )
    case = Case(
        case_id="OCTX-CASE-1",
        customer_id=customer.customer_id,
        case_type="OPEN",
    )
    db_session.add(customer)
    db_session.add(case)
    db_session.commit()
    return customer.customer_id, case.case_id


def _add_outcome(db_session, *, case_id, outcome_id, observed_at, state="POSITIVE"):
    from app.models.outcome_assessment import OutcomeAssessment

    row = OutcomeAssessment(
        outcome_assessment_id=outcome_id,
        case_id=case_id,
        result_state=state,
        provenance="CUSTOMER",
        actor_id="OCTX-CUST-1",
        observed_at=observed_at,
    )
    db_session.add(row)
    db_session.commit()
    return row


def test_outcome_context_projection_preserves_trace_and_order(db_session):
    from app.models.case import Case
    from app.services.outcome_assessment_context_service import OutcomeAssessmentContextService

    customer_id, case_id = _seed_customer_case(db_session)
    newer = datetime.now(timezone.utc)
    older = newer - timedelta(days=1)
    _add_outcome(
        db_session,
        case_id=case_id,
        outcome_id="OCTX-OA-OLD",
        observed_at=older,
        state="NO_BENEFIT",
    )
    _add_outcome(
        db_session,
        case_id=case_id,
        outcome_id="OCTX-OA-NEW",
        observed_at=newer,
        state="POSITIVE",
    )

    case = db_session.get(Case, case_id)
    result = OutcomeAssessmentContextService(db_session).build_for_case(case)

    assert result["source"] == "OUTCOME_ASSESSMENT_HISTORY"
    assert result["mode"] == "ADDITIVE_LONGITUDINAL_CONTEXT"
    assert result["case_id"] == case_id
    assert result["customer_id"] == customer_id
    assert [row["outcome_assessment_id"] for row in result["records"]] == [
        "OCTX-OA-NEW",
        "OCTX-OA-OLD",
    ]

    required = {
        "outcome_assessment_id",
        "case_id",
        "result_state",
        "observed_at",
        "created_at",
        "provenance",
        "actor_id",
        "product_id",
        "recommendation_id",
        "feedback_id",
        "follow_up_id",
    }
    assert required.issubset(result["records"][0].keys())
    assert result["records"][0]["result_state"] == "POSITIVE"
    assert result["records"][1]["result_state"] == "NO_BENEFIT"


def test_outcome_context_preserves_unknown_and_not_used(db_session):
    from app.models.case import Case
    from app.services.outcome_assessment_context_service import OutcomeAssessmentContextService

    _, case_id = _seed_customer_case(db_session)
    now = datetime.now(timezone.utc)
    _add_outcome(db_session, case_id=case_id, outcome_id="OCTX-OA-UNKNOWN", observed_at=now, state="UNKNOWN")
    _add_outcome(
        db_session,
        case_id=case_id,
        outcome_id="OCTX-OA-NOTUSED",
        observed_at=now - timedelta(minutes=1),
        state="NOT_USED",
    )

    case = db_session.get(Case, case_id)
    result = OutcomeAssessmentContextService(db_session).build_for_case(case)
    states = {row["result_state"] for row in result["records"]}

    assert states == {"UNKNOWN", "NOT_USED"}


def test_recommendation_boundary_receives_additive_outcome_context(client, db_session):
    customer_id, case_id = _seed_customer_case(db_session)
    _add_outcome(
        db_session,
        case_id=case_id,
        outcome_id="OCTX-OA-TRACE",
        observed_at=datetime.now(timezone.utc),
        state="ADVERSE_REACTION",
    )

    captured = {}

    def fake_generate(self, requested_case_id, customer_profile):
        captured["case_id"] = requested_case_id
        captured["profile"] = customer_profile
        return []

    with patch(
        "app.api.routers.recommendations.RecommendationFacade.generate",
        new=fake_generate,
    ):
        response = client.post(
            "/api/v1/recommendations/generate",
            headers=_headers(customer_id),
            json={"case_id": case_id, "customer_profile": {}},
        )

    assert response.status_code == 200, response.text
    assert captured["case_id"] == case_id

    context = captured["profile"]["_outcome_assessment_context"]
    assert context["mode"] == "ADDITIVE_LONGITUDINAL_CONTEXT"
    assert context["records"][0]["outcome_assessment_id"] == "OCTX-OA-TRACE"
    assert context["records"][0]["case_id"] == case_id
    assert context["records"][0]["provenance"] == "CUSTOMER"
    assert "outcome_assessment" not in captured["profile"]["_profile_fact_context"]


def test_foreign_case_cannot_expose_outcome_context(client, db_session):
    from app.models.customer import Customer
    from app.models.case import Case

    owner_id, _ = _seed_customer_case(db_session)
    foreign = Customer(
        customer_id="OCTX-CUST-2",
        name="Other Customer",
        consent_to_store_data=1,
    )
    foreign_case = Case(
        case_id="OCTX-CASE-2",
        customer_id=foreign.customer_id,
        case_type="OPEN",
    )
    db_session.add_all([foreign, foreign_case])
    db_session.commit()

    response = client.post(
        "/api/v1/recommendations/generate",
        headers=_headers(owner_id),
        json={"case_id": foreign_case.case_id, "customer_profile": {}},
    )

    assert response.status_code == 403
