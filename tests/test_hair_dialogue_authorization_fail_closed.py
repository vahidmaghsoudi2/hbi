"""Authorization dependency failure handling for the synthetic Hair dialogue route."""

from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import create_access_token
from app.models.user_role import ROLE_REVIEWER_QA, UserRole


def test_role_lookup_database_error_fails_closed_without_diagnostic_leakage(
    client, db_session, monkeypatch
):
    subject_id = "hair-dialogue-db-failure-test-user"
    db_session.add(
        UserRole(
            user_role_id="HAIR-DIALOGUE-DB-FAILURE-ROLE",
            subject_id=subject_id,
            role=ROLE_REVIEWER_QA,
        )
    )
    db_session.commit()

    def fail_role_lookup(_db, _subject_id):
        raise SQLAlchemyError("synthetic database connection diagnostic")

    import app.api.routers.hair_dialogue as hair_dialogue

    monkeypatch.setattr(hair_dialogue, "get_roles_for_subject", fail_role_lookup)
    token = create_access_token({"sub": subject_id})
    response = client.post(
        "/api/v1/hair/dialogue/turn",
        json={
            "action": "ANSWER_QUESTION",
            "state": {
                "case_id": "SYNTHETIC-AUTH-FAILURE-001",
                "case_version": "case-v1",
                "goal_version": "goal-v1",
                "rejected_proposal_ids": [],
                "client_decision": "NONE",
            },
            "question_code": "STATUS_REASON",
            "answer_code": "STATUS_REASON",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Internal authorization service is temporarily unavailable"
    }
    assert "synthetic database connection diagnostic" not in response.text
