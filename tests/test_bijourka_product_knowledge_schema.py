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


def test_first_bijourka_10_3_record_is_identity_only_and_fails_closed():
    records_path = (
        Path(__file__).resolve().parents[1]
        / "docs/homepage/encyclopedia/hair-color/catalog/"
        / "bijourka_product_knowledge.records.json"
    )
    payload = json.loads(records_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "hbi.bijourka-product-knowledge.v1"
    assert payload["catalog_reference"]["authority"] == "PRODUCT_OWNER_APPROVED"
    assert len(payload["records"]) == 1

    record = payload["records"][0]
    assert record["catalog_identity"] == {
        "brand": "بیجورکا",
        "series": "زیتونی",
        "shade_number": "۱۰.۳",
        "shade_name": "بلوند زیتونی پلاتینه",
    }
    assert record["formulation"]["status"] == "UNKNOWN"
    assert record["formulation"]["ingredient_list"] == []
    assert record["expert_review"]["status"] == "NOT_REVIEWED"
    assert record["record_status"] == "DRAFT"
    assert any(
        gap["gap_type"] == "KNOWLEDGE_GAP"
        and "formulation.ingredient_list" in gap["field"]
        and "CHEMICAL_GUIDANCE" in gap["blocks"]
        for gap in record["evidence_gaps"]
    )
    assert all(
        claim["claim_scope"] == "IDENTITY"
        for claim in record["claims"]
    )

def test_bijourka_10_3_record_preserves_retail_metadata_conflict_without_reclassifying_shade():
    records_path = (
        Path(__file__).resolve().parents[1]
        / "docs/homepage/encyclopedia/hair-color/catalog/"
        / "bijourka_product_knowledge.records.json"
    )
    payload = json.loads(records_path.read_text(encoding="utf-8"))
    record = next(
        item
        for item in payload["records"]
        if item["record_id"] == "BIJOURKA-KNOWLEDGE-10-3-MATT"
    )

    assert record["catalog_identity"]["series"] == "زیتونی"
    assert record["catalog_identity"]["shade_number"] == "۱۰.۳"

    conflict = next(
        claim
        for claim in record["claims"]
        if claim["claim_id"] == "RETAIL-METADATA-QUALITY-ALERT-1766203352"
    )
    assert conflict["claim_type"] == "CONFLICT"
    assert conflict["evidence_status"] == "CONFLICTING"
    assert {
        "BIJOURKA-RETAIL-LISTING-TECHNOLIFE-7-3-100ML",
        "BIJOURKA-RETAIL-LISTING-TECHNOLIFE-8-3-100ML",
        "BIJOURKA-RETAIL-LISTING-TECHNOLIFE-9-3-100ML",
        "BIJOURKA-RETAIL-LISTING-TECHNOLIFE-10-3-100ML",
    }.issubset(set(conflict["evidence_ids"]))

    assert any(
        gap["gap_type"] == "SOURCE_CONFLICT"
        and gap["field"] == "retail_listing.technical_attributes/license_number"
        and "CHEMICAL_GUIDANCE" in gap["blocks"]
        for gap in record["evidence_gaps"]
    )

