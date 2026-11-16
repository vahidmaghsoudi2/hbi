from __future__ import annotations

from dataclasses import replace

from app.domain.hair_catalog_identity_lookup import (
    CatalogIdentity,
    build_catalog_decision_output,
    decide_catalog_output_presentation,
    lookup_catalog_identity,
)
from app.domain.hair_catalog_provider import load_approved_hair_catalog_reference


def _bijourka_10_3() -> CatalogIdentity:
    return CatalogIdentity(
        brand="بیجورکا",
        series="زیتونی",
        shade_number="۱۰.۳",
        shade_name="بلوند زیتونی پلاتینه",
    )


def test_po_approved_bijourka_identity_matches_without_publisher_edition():
    loaded = load_approved_hair_catalog_reference()
    assert loaded is not None
    reference_id, reference = loaded
    identity = _bijourka_10_3()

    assert reference.edition_label is None
    assert reference.captured_at is None

    result = lookup_catalog_identity(
        service_kind="CATALOG_READY",
        expected=identity,
        observed=identity,
        reference=reference,
    )

    assert result.outcome == "MATCH"
    assert result.reason_code == "EXACT_CATALOG_IDENTITY_MATCH"
    assert result.traceability_complete is True
    assert result.source_edition == reference.snapshot_id
    assert result.source_captured_at == reference.snapshot_captured_at

    output = build_catalog_decision_output(
        service_kind="CATALOG_READY",
        result=result,
        reference_id=reference_id,
        reference=reference,
        expected=identity,
        observed=identity,
        provenance=("PO_APPROVED_BIJOURKA_CATALOG",),
        evidence_reference_pointers=(reference.url,),
        decision_output_id="synthetic-bijourka-identity-001",
    )
    presentation = decide_catalog_output_presentation(output)

    assert presentation.display_allowed is True
    assert presentation.status == "IDENTITY_MATCH_DISPLAYABLE"


def test_bijourka_approval_does_not_depend_on_raeaka_publisher_host():
    loaded = load_approved_hair_catalog_reference()
    assert loaded is not None
    _, reference = loaded
    identity = _bijourka_10_3()
    po_owned_reference = replace(reference, url="hbi://po-approved/bijourka-catalog")

    result = lookup_catalog_identity(
        service_kind="CATALOG_READY",
        expected=identity,
        observed=identity,
        reference=po_owned_reference,
    )

    assert result.outcome == "MATCH"
    assert result.traceability_complete is True


def test_identity_lookup_still_stops_when_hbi_snapshot_lineage_is_missing():
    loaded = load_approved_hair_catalog_reference()
    assert loaded is not None
    _, reference = loaded
    identity = _bijourka_10_3()

    unversioned_reference = replace(reference, snapshot_id=None)
    result = lookup_catalog_identity(
        service_kind="CATALOG_READY",
        expected=identity,
        observed=identity,
        reference=unversioned_reference,
    )

    assert result.outcome == "STOP"
    assert result.stop_class == "KNOWLEDGE_GAP"
    assert result.reason_code == "APPROVED_CATALOG_REFERENCE_NOT_ESTABLISHED"
    assert result.traceability_complete is False
