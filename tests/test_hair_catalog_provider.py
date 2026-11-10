from __future__ import annotations

import hashlib

from app.domain.hair_catalog_provider import (
    EXPECTED_DATA_ROWS,
    _catalog_path,
    load_approved_hair_catalog_reference,
)


def test_approved_catalog_provider_loads_exact_88_row_artifact():
    path = _catalog_path()
    raw = path.read_bytes()
    reference = load_approved_hair_catalog_reference()

    assert reference is not None
    reference_id, metadata = reference
    digest = hashlib.sha256(raw).hexdigest()

    assert reference_id == metadata.snapshot_id
    assert reference_id.startswith("hbi-hair-catalog-snapshot-")
    assert metadata.content_sha256 == digest
    assert metadata.source_kind == "RAEAKA_BIJOURKA_CATALOG"
    assert metadata.approval_status == "PO_APPROVED"
    assert metadata.edition_label is None
    assert metadata.captured_at is None
    assert len(raw.decode("utf-8-sig").splitlines()) - 1 == EXPECTED_DATA_ROWS


def test_approved_catalog_provider_does_not_invent_version_metadata():
    reference = load_approved_hair_catalog_reference()

    assert reference is not None
    _, metadata = reference
    assert metadata.edition_label is None
    assert metadata.captured_at is None
