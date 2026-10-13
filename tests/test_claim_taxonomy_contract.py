import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.core.claim_taxonomy import ALLOWED_CLAIM_TYPES, CLAIM_TYPES, normalize_claim_type_value
from app.interface.schemas import EvidenceCreate, EvidenceUpdate, ResearchAssertion
from app.services.evidence_service import EvidenceService


@pytest.mark.parametrize(
    "claim_type",
    ["FACT", "MANUFACTURER_CLAIM", "EVIDENCE", "INFERENCE", "UNKNOWN", "CONFLICT"],
)
def test_canonical_claim_types_are_accepted_by_api_schema(claim_type):
    payload = EvidenceCreate(
        product_id="TAXONOMY-001",
        claim="sample claim",
        source_type="MANUFACTURER",
        source_reference="test://taxonomy",
        claim_type=claim_type,
    )
    assert payload.claim_type == claim_type
    assert claim_type in CLAIM_TYPES
    assert claim_type in ALLOWED_CLAIM_TYPES


@pytest.mark.parametrize("model", [EvidenceCreate, ResearchAssertion])
def test_legacy_or_unsupported_claim_type_is_rejected_by_api_schema(model):
    payload = {
        "product_id": "TAXONOMY-001",
        "claim": "sample claim",
        "source_type": "MANUFACTURER",
        "source_reference": "test://taxonomy",
        "claim_type": "BENEFIT",
    }
    if model is ResearchAssertion:
        payload.pop("product_id")
    with pytest.raises(PydanticValidationError):
        model(**payload)


@pytest.mark.parametrize("raw", [" fact ", "manufacturer_claim", "Evidence", "unknown"])
def test_schema_normalizes_supported_claim_type_values(raw):
    payload = EvidenceCreate(
        product_id="TAXONOMY-002",
        claim="sample claim",
        source_type="MANUFACTURER",
        source_reference="test://taxonomy",
        claim_type=raw,
    )
    assert payload.claim_type == raw.strip().upper()


def test_update_schema_normalizes_claim_type_and_preserves_omission():
    assert EvidenceUpdate(claim_type=" conflict ").claim_type == "CONFLICT"
    assert EvidenceUpdate().claim_type is None


def test_research_assertion_normalizes_claim_type():
    assert ResearchAssertion(
        claim="sample claim", source_type="MANUFACTURER",
        source_reference="test://taxonomy", claim_type=" inference "
    ).claim_type == "INFERENCE"


def test_taxonomy_exports_one_compatible_vocabulary():
    assert CLAIM_TYPES is ALLOWED_CLAIM_TYPES
    assert normalize_claim_type_value(" manufacturer_claim ") == "MANUFACTURER_CLAIM"
    assert normalize_claim_type_value(None) == "UNKNOWN"


def test_service_rejects_unsupported_claim_type_before_persistence():
    service = EvidenceService.__new__(EvidenceService)
    with pytest.raises(ValidationError, match="Unsupported claim_type"):
        service._validate_claim_boundary("BENEFIT", "MANUFACTURER")


def test_fact_still_requires_independent_source():
    service = EvidenceService.__new__(EvidenceService)
    with pytest.raises(ValidationError, match="FACT claims require independent verification"):
        service._validate_claim_boundary("FACT", "MANUFACTURER")
