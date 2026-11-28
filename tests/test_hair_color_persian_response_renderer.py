from app.hair_color.persian_response_renderer import render_persian_response


def test_safety_stop_renders_non_executable_persian_message():
    rendered = render_persian_response({
        "consultation_status": "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
        "missing_information": [],
    })
    assert "ایمنی" in rendered["title"]
    assert rendered["options"] == []
    assert rendered["execution_authorized"] is False


def test_missing_fields_are_deduplicated_and_rendered_without_advice():
    rendered = render_persian_response({
        "consultation_status": "NEEDS_INFORMATION_OR_TEST",
        "missing_information": [
            {"field": "history", "reason": "synthetic"},
            {"field": "history", "reason": "duplicate"},
            "current_state",
        ],
    })
    assert rendered["missing_fields"] == ["history", "current_state"]
    assert rendered["options"] == []
    assert rendered["execution_authorized"] is False
    assert "اطلاعات" in rendered["title"]


def test_knowledge_gap_routes_to_specialist_and_never_invents_options():
    rendered = render_persian_response({
        "consultation_status": "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        "missing_information": [],
    })
    assert "متخصص" in rendered["title"]
    assert rendered["options"] == []
    assert rendered["execution_authorized"] is False


def test_unknown_status_fails_closed_with_neutral_message():
    rendered = render_persian_response({
        "consultation_status": "UNRECOGNIZED",
        "missing_information": [],
    })
    assert "مشخص نیست" in rendered["title"]
    assert rendered["options"] == []
    assert rendered["execution_authorized"] is False
