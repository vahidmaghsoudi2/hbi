from types import SimpleNamespace

from app.interface.facades import _to_product_dto


def test_product_dto_exposes_review_lifecycle_fields():
    product = SimpleNamespace(
        product_id="DTO-SKIN-001",
        brand="Test Brand",
        product_name="Test Skin Product",
        identity_status="NEEDS_REVIEW",
        qa_verdict="PENDING",
        status="DRAFT",
        product_line="SKIN",
        variant=None,
        size_value=50,
        size_unit="ml",
    )

    dto = _to_product_dto(product)

    assert dto.status == "DRAFT"
    assert dto.product_line == "SKIN"


def test_product_dto_preserves_legacy_null_product_line():
    product = SimpleNamespace(
        product_id="DTO-LEGACY-001",
        brand="Legacy Brand",
        product_name="Legacy Product",
        identity_status="NEEDS_REVIEW",
        qa_verdict="PENDING",
        status="DRAFT",
        variant=None,
        size_value=None,
        size_unit=None,
    )

    dto = _to_product_dto(product)

    assert dto.status == "DRAFT"
    assert dto.product_line is None
