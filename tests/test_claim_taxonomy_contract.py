import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.core.claim_taxonomy import CLAIM_TYPES
from app.interface.schemas import EvidenceCreate, ResearchAssertion
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


def test_service_rejects_unsupported_claim_type_before_persistence():
    service = EvidenceService.__new__(EvidenceService)
    with pytest.raises(ValidationError, match="Unsupported claim_type"):
        service._validate_claim_boundary("BENEFIT", "MANUFACTURER")


def test_fact_still_requires_independent_source():
    service = EvidenceService.__new__(EvidenceService)
    with pytest.raises(ValidationError, match="FACT claims require independent verification"):
        service._validate_claim_boundary("FACT", "MANUFACTURER")
