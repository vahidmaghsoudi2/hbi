import pytest

from app.hair_color.knowledge_bundle_provenance import (
    KnowledgeBundleValidationError,
    validate_knowledge_bundle,
)


def valid_bundle():
    return {
        "bundle_ref": "BUNDLE-SYN-01",
        "product_identity": {
            "product_id": "PRODUCT-SYN-01",
            "brand": "Synthetic Brand",
            "market": "Synthetic Market",
            "product_version": "SYN-V1",
        },
        "sources": [{
            "source_id": "SRC-SYN-01",
            "publisher": "Synthetic Publisher",
            "title": "Synthetic source document",
            "source_version": "SYN-REV-1",
            "applicability": "Synthetic scope only",
        }],
        "claims": [{
            "claim_id": "CLAIM-SYN-01",
            "claim_text": "Synthetic placeholder claim; no domain statement.",
            "source_refs": ["SRC-SYN-01"],
        }],
    }


def test_metadata_valid_bundle_is_not_activated_or_publishable():
    result = validate_knowledge_bundle(valid_bundle())
    assert result["metadata_valid"] is True
    assert result["publishable"] is False
    assert result["activation_allowed"] is False
    assert result["status"] == "READY_FOR_SPECIALIST_REVIEW"


def test_approval_metadata_recorded_does_not_enable_activation():
    bundle = valid_bundle()
    bundle["specialist_approval"] = {
        "status": "APPROVED",
        "approved_by": "Synthetic Reviewer",
        "approved_at": "SYNTHETIC-TIME",
        "scope": "Synthetic test scope",
    }
    result = validate_knowledge_bundle(bundle)
    assert result["specialist_approval_record_valid"] is True
    assert result["publishable"] is False
    assert result["activation_allowed"] is False
    assert result["status"] == "APPROVAL_METADATA_RECORDED"


@pytest.mark.parametrize("missing", ["product_id", "brand", "market", "product_version"])
def test_missing_exact_product_identity_field_rejected(missing):
    bundle = valid_bundle()
    del bundle["product_identity"][missing]
    with pytest.raises(KnowledgeBundleValidationError, match="product_identity"):
        validate_knowledge_bundle(bundle)


def test_claim_cannot_reference_unknown_source():
    bundle = valid_bundle()
    bundle["claims"][0]["source_refs"] = ["SRC-NOT-FOUND"]
    with pytest.raises(KnowledgeBundleValidationError, match="unknown source"):
        validate_knowledge_bundle(bundle)


def test_duplicate_source_ids_rejected():
    bundle = valid_bundle()
    bundle["sources"].append(dict(bundle["sources"][0]))
    with pytest.raises(KnowledgeBundleValidationError, match="unique"):
        validate_knowledge_bundle(bundle)


def test_missing_claim_or_source_collection_fails_closed():
    bundle = valid_bundle()
    bundle["sources"] = []
    with pytest.raises(KnowledgeBundleValidationError, match="source"):
        validate_knowledge_bundle(bundle)
    bundle = valid_bundle()
    bundle["claims"] = []
    with pytest.raises(KnowledgeBundleValidationError, match="claim"):
        validate_knowledge_bundle(bundle)


def test_incomplete_approval_metadata_is_not_recognized_as_approval():
    bundle = valid_bundle()
    bundle["specialist_approval"] = {"status": "APPROVED", "approved_by": "Reviewer"}
    result = validate_knowledge_bundle(bundle)
    assert result["specialist_approval_record_valid"] is False
    assert result["activation_allowed"] is False


@pytest.mark.parametrize("missing", ["source_id", "publisher", "title", "source_version", "source_locator", "retrieved_at", "applicability"])
def test_missing_source_provenance_field_rejected(missing):
    bundle = valid_bundle()
    del bundle["sources"][0][missing]
    with pytest.raises(KnowledgeBundleValidationError, match="source."):
        validate_knowledge_bundle(bundle)
