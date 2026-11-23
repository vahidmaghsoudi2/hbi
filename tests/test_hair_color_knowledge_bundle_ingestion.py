import json
import pytest

from app.hair_color.knowledge_bundle_ingestion import (
    KnowledgeBundleImportError,
    ingest_knowledge_bundle,
)


def fixture_bundle():
    return {
        "bundle_ref": "BUNDLE-SYN-INGEST",
        "product_identity": {
            "product_id": "PRODUCT-SYN-INGEST",
            "brand": "Synthetic Brand",
            "market": "Synthetic Market",
            "product_version": "SYN-V1",
        },
        "sources": [{
            "source_id": "SRC-SYN-INGEST",
            "publisher": "Synthetic Publisher",
            "title": "Synthetic reference",
            "source_version": "SYN-REV-1",
            "source_locator": "synthetic://source",
            "retrieved_at": "SYNTHETIC-TIME",
            "applicability": "Synthetic scope only",
        }],
        "claims": [{
            "claim_id": "CLAIM-SYN-INGEST",
            "claim_text": "Synthetic placeholder, no domain claim",
            "source_refs": ["SRC-SYN-INGEST"],
        }],
    }


def envelope():
    return {"bundle_schema_version": "1.0", "bundle": fixture_bundle()}


def test_ingest_mapping_returns_inactive_metadata_only():
    result = ingest_knowledge_bundle(envelope())
    assert result["imported"] is True
    assert result["metadata_valid"] is True
    assert result["status"] == "INACTIVE_REVIEW_REQUIRED"
    assert result["activation_allowed"] is False
    assert result["publishable"] is False


def test_json_string_ingestion_matches_mapping():
    result = ingest_knowledge_bundle(json.dumps(envelope()))
    assert result["bundle_ref"] == "BUNDLE-SYN-INGEST"
    assert result["claim_count"] == 1
    assert not result["activation_allowed"]


@pytest.mark.parametrize("payload", ["{bad json", "null", 5, [], {"bundle_schema_version": "2.0", "bundle": fixture_bundle()}])
def test_invalid_envelope_rejected(payload):
    with pytest.raises(KnowledgeBundleImportError):
        ingest_knowledge_bundle(payload)


def test_provenance_error_is_wrapped_and_fails_closed():
    data = envelope()
    data["bundle"]["claims"][0]["source_refs"] = ["missing"]
    with pytest.raises(KnowledgeBundleImportError, match="provenance validation failed"):
        ingest_knowledge_bundle(data)
