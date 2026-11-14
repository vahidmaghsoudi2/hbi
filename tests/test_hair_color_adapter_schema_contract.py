"""Keep the draft JSON Schema aligned with the executable adapter contract.

These are structural parity checks only. They do not promote Draft 0.2 to a
production protocol or validate hair-colour chemistry.
"""
import json
from pathlib import Path

from app.hair_color.adapter import (
    CONSULTATION_STATES,
    ENGINE_STATES,
    OPERATIONS,
    REASON_CODES,
    _REQUEST_FIELDS,
    _RESPONSE_FIELDS,
)


SCHEMA_PATH = Path(__file__).parent / "schemas" / "hair-color-adapter-0.2-draft.schema.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_draft_schema_enums_match_runtime_adapter_contract():
    schema = load_schema()
    request = schema["$defs"]["request"]
    response = schema["$defs"]["response"]

    assert request["properties"]["contract_version"]["const"] == "0.2-draft"
    assert set(request["properties"]["operation"]["enum"]) == OPERATIONS
    assert set(response["properties"]["engine_state"]["enum"]) == ENGINE_STATES
    assert set(response["properties"]["consultation_status"]["enum"]) == CONSULTATION_STATES
    assert set(response["properties"]["reason_codes"]["items"]["enum"]) == REASON_CODES


def test_draft_schema_keeps_candidate_and_duplicate_reference_constraints():
    response = load_schema()["$defs"]["response"]

    assert response["properties"]["options"]["maxItems"] == 3
    assert response["properties"]["reason_codes"]["uniqueItems"] is True
    assert response["properties"]["evidence_refs"]["uniqueItems"] is True


def test_schema_required_fields_match_the_executable_adapter_envelopes():
    schema = load_schema()
    request = schema["$defs"]["request"]
    response = schema["$defs"]["response"]

    assert set(request["required"]) == set(_REQUEST_FIELDS)
    assert set(request["properties"]) == set(_REQUEST_FIELDS)
    assert set(response["required"]) == set(_RESPONSE_FIELDS)
    assert set(response["properties"]) == set(_RESPONSE_FIELDS)


def test_schema_declares_the_same_top_level_shapes_expected_by_runtime():
    schema = load_schema()
    request = schema["$defs"]["request"]["properties"]
    response = schema["$defs"]["response"]["properties"]

    for field in ("case_context", "policy_context"):
        assert request[field]["type"] == "object"
    assert request["evidence_context"]["type"] == "array"
    assert request["evidence_context"]["items"]["type"] == "object"

    for field in ("reason_codes", "options", "missing_information", "evidence_refs", "limitations"):
        assert response[field]["type"] == "array"
    for field in ("next_step",):
        assert response[field]["type"] == "object"


def test_schema_string_and_version_definitions_keep_runtime_minimums():
    schema = load_schema()
    nonempty = schema["$defs"]["nonEmptyString"]
    version = schema["$defs"]["version"]

    assert nonempty["type"] == "string"
    assert nonempty["minLength"] == 1
    assert nonempty["pattern"] == r"\\S"
    assert version["type"] == "integer"
    assert version["minimum"] == 1


def test_schema_candidate_and_evidence_items_preserve_required_shapes():
    schema = load_schema()
    request = schema["$defs"]["request"]["properties"]
    response = schema["$defs"]["response"]["properties"]

    evidence_ref = request["evidence_context"]["items"]["properties"]["evidence_ref"]
    assert evidence_ref == {"$ref": "#/$defs/nonEmptyString"}
    assert response["options"]["items"]["type"] == "object"
    assert response["evidence_refs"]["items"] == {"$ref": "#/$defs/nonEmptyString"}


def test_schema_top_level_union_resolves_only_request_and_response_definitions():
    schema = load_schema()

    assert schema["oneOf"] == [
        {"$ref": "#/$defs/request"},
        {"$ref": "#/$defs/response"},
    ]
    assert schema["$defs"]["request"]["type"] == "object"
    assert schema["$defs"]["response"]["type"] == "object"


def test_schema_remains_explicitly_draft_and_does_not_claim_production_readiness():
    schema = load_schema()

    assert schema["title"] == "HBI Hair Color Adapter Contract 0.2-draft"
    assert "not a production protocol" in schema["description"]
