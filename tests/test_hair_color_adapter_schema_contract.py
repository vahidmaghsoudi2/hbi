"""Keep the draft JSON Schema aligned with the executable adapter enums.

This is a structural drift test only; it does not make the draft schema a
production protocol or validate hair-colour science.
"""
import json
from pathlib import Path

from app.hair_color.adapter import (
    CONSULTATION_STATES,
    ENGINE_STATES,
    OPERATIONS,
    REASON_CODES,
)


SCHEMA_PATH = Path(__file__).parent / "schemas" / "hair-color-adapter-0.2-draft.schema.json"


def test_draft_schema_enums_match_runtime_adapter_contract():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    request = schema["$defs"]["request"]
    response = schema["$defs"]["response"]

    assert request["properties"]["contract_version"]["const"] == "0.2-draft"
    assert set(request["properties"]["operation"]["enum"]) == OPERATIONS
    assert set(response["properties"]["engine_state"]["enum"]) == ENGINE_STATES
    assert set(response["properties"]["consultation_status"]["enum"]) == CONSULTATION_STATES
    assert set(response["properties"]["reason_codes"]["items"]["enum"]) == REASON_CODES


def test_draft_schema_keeps_candidate_and_duplicate_reference_constraints():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    response = schema["$defs"]["response"]

    assert response["properties"]["options"]["maxItems"] == 3
    assert response["properties"]["reason_codes"]["uniqueItems"] is True
    assert response["properties"]["evidence_refs"]["uniqueItems"] is True
