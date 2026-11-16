from __future__ import annotations

import json
from pathlib import Path


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs/homepage/encyclopedia/hair-color/catalog/"
    / "bijourka_product_knowledge.schema.json"
)


def test_bijourka_product_knowledge_schema_is_versioned_and_closed():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_version"]["const"] == (
        "hbi.bijourka-product-knowledge.v1"
    )
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "schema_version",
        "catalog_reference",
        "records",
    }


def test_schema_keeps_catalog_identity_separate_from_product_chemistry():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record = schema["$defs"]["productRecord"]

    assert set(record["required"]) == {
        "record_id",
        "catalog_identity",
        "product_context",
        "formulation",
        "claims",
        "evidence",
        "expert_review",
        "evidence_gaps",
        "record_status",
    }
    assert set(record["properties"]["catalog_identity"]["required"]) == {
        "brand",
        "series",
        "shade_number",
        "shade_name",
    }
    assert "status" in record["properties"]["formulation"]["required"]
    assert "market_region" in record["properties"]["product_context"]["required"]
    assert "lot" in record["properties"]["product_context"]["required"]
    assert "formula_version" in record["properties"]["product_context"]["required"]


def test_schema_distinguishes_claim_types_evidence_and_review_state():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record = schema["$defs"]["productRecord"]

    claim_types = set(
        record["properties"]["claims"]["items"]["properties"]["claim_type"]["enum"]
    )
    assert {
        "MANUFACTURER_CLAIM",
        "EVIDENCE_SUPPORTED_CLAIM",
        "SPECIALIST_ASSESSMENT",
        "INFERENCE",
        "UNKNOWN",
        "CONFLICT",
    }.issubset(claim_types)

    review_states = set(
        record["properties"]["expert_review"]["properties"]["status"]["enum"]
    )
    assert {"NOT_REVIEWED", "PENDING", "ACCEPTED", "REJECTED", "LIMITED"} == review_states


def test_schema_has_explicit_fail_closed_gap_categories_for_decision_use():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record = schema["$defs"]["productRecord"]

    gap_types = set(
        record["properties"]["evidence_gaps"]["items"]["properties"]["gap_type"]["enum"]
    )
    assert gap_types == {
        "DATA_GAP",
        "KNOWLEDGE_GAP",
        "SOURCE_CONFLICT",
        "EXPERT_REVIEW_REQUIRED",
    }

    blocked_uses = set(
        record["properties"]["evidence_gaps"]["items"]["properties"]["blocks"]["items"]["enum"]
    )
    assert {
        "CHEMICAL_GUIDANCE",
        "SAFETY_ASSESSMENT",
        "COMPATIBILITY_ASSESSMENT",
        "FORMULA_SELECTION",
        "PROCESSING_PARAMETERS",
        "COLOR_OUTCOME_PREDICTION",
    }.issubset(blocked_uses)
