import pytest

from app.hair_color.intake import HairColorIntakeError, build_intake_request, get_intake_field_labels
from app.hair_color.consultation import run_consultation_from_intake, run_consultation_from_intake_persian


def complete_intake():
    return {
        "current_hair_state": "Synthetic current-state description",
        "desired_result": "Synthetic target description",
        "service_history": "Synthetic service history",
        "product_context": "Synthetic product details",
    }


def meta(**overrides):
    values = {"request_id": "REQ-INTAKE-SYN", "case_ref": "CASE-INTAKE-SYN"}
    values.update(overrides)
    return values


def test_missing_fields_are_derived_and_reported_explicitly():
    request = build_intake_request({"desired_result": "synthetic"}, **meta())
    missing = request["case_context"]["missing_fields"]
    assert set(missing) == {"current_hair_state", "service_history", "product_context"}
    assert request["case_context"]["intake_complete"] is False


def test_reference_context_is_optional_and_labels_are_stable_copy():
    request = build_intake_request(complete_intake(), **meta())
    assert request["case_context"]["missing_fields"] == []
    assert request["case_context"]["intake_complete"] is True
    assert "reference_context" not in request["case_context"]["intake"]
    labels = get_intake_field_labels()
    assert labels["desired_result"]
    labels.clear()
    assert get_intake_field_labels()


def test_optional_reference_context_is_kept_when_supplied():
    request = build_intake_request({**complete_intake(), "reference_context": "Synthetic reference"}, **meta())
    assert request["case_context"]["intake"]["reference_context"] == "Synthetic reference"


@pytest.mark.parametrize("value", [None, "", "   ", 7, False])
def test_invalid_required_intake_values_are_missing_not_coerced(value):
    request = build_intake_request({**complete_intake(), "current_hair_state": value}, **meta())
    assert "current_hair_state" in request["case_context"]["missing_fields"]


def test_builder_rejects_bad_metadata_and_safety_flag():
    with pytest.raises(HairColorIntakeError):
        build_intake_request(complete_intake(), **meta(case_version=True))
    with pytest.raises(HairColorIntakeError):
        build_intake_request(complete_intake(), **meta(safety_concern="yes"))


def test_public_intake_api_fails_closed_with_missing_fields():
    result = run_consultation_from_intake({"desired_result": "Synthetic target"}, **meta())
    assert result["reason_codes"] == ["DATA_GAP"]
    assert result["options"] == []
    assert result["engine_state"] == "NEEDS_MORE_INFORMATION"


def test_complete_intake_still_does_not_unlock_unvalidated_domain_advice():
    result = run_consultation_from_intake(complete_intake(), **meta())
    assert result["reason_codes"] == ["KNOWLEDGE_GAP"]
    assert result["options"] == []
    assert result["consultation_status"] == "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW"


def test_safety_flag_routes_to_stop():
    result = run_consultation_from_intake(complete_intake(), **meta(safety_concern=True))
    assert result["reason_codes"] == ["SAFETY_CONCERN"]
    assert result["consultation_status"] == "SAFETY_STOP_NO_EXECUTION_SUGGESTION"
    assert result["options"] == []


def test_persian_public_intake_wrapper_keeps_no_options_and_no_execution():
    result = run_consultation_from_intake_persian({"desired_result": "Synthetic"}, **meta())
    assert result["presentation"]["missing_fields"]
    assert result["presentation"]["options"] == []
    assert result["execution_authorized"] is False
