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
    assert metadata.snapshot_captured_at == "2026-11-10T18:57:00Z"
    assert metadata.ingestion_id == "hbi-hair-catalog-ingestion-20261110-185700z-01"
    assert metadata.snapshot_validation_status == "VALIDATED_ON_LOAD"
    assert metadata.snapshot_id == "hbi-hair-catalog-snapshot-20261110-185700z"
    assert len(raw.decode("utf-8-sig").splitlines()) - 1 == EXPECTED_DATA_ROWS
    from app.domain.hair_catalog_provider import EXPECTED_SERIES
    import csv
    from io import StringIO

    rows = list(csv.DictReader(StringIO(raw.decode("utf-8-sig"))))
    assert {row["سری محصول"] for row in rows} == set(EXPECTED_SERIES)
    assert len(EXPECTED_SERIES) == 19
    actual_series_codes = {
        series: {row["شماره رنگ"] for row in rows if row["سری محصول"] == series}
        for series in EXPECTED_SERIES
    }
    assert actual_series_codes == {
        series: set(codes)
        for series, codes in __import__(
            "app.domain.hair_catalog_provider",
            fromlist=["EXPECTED_SERIES_CODES"],
        ).EXPECTED_SERIES_CODES.items()
    }
    assert sum(len(codes) for codes in actual_series_codes.values()) == 88
    assert {series: len(codes) for series, codes in actual_series_codes.items()} == {
        "طبیعی": 10,
        "طبیعی اکسترا": 5,
        "خاکستری": 8,
        "دودی": 5,
        "زیتونی": 6,
        "طلایی": 6,
        "بژ": 4,
        "نسکافه ای": 4,
        "آلبالویی": 3,
        "شکلاتی": 4,
        "عسلی": 3,
        "فندقی": 4,
        "شرابی": 4,
        "قرمز": 4,
        "عروسکی": 3,
        "بیسکویتی": 2,
        "کاپوچینو": 2,
        "ترکیبی": 8,
        "واریاسیون": 3,
    }


def test_approved_catalog_provider_does_not_invent_version_metadata():
    reference = load_approved_hair_catalog_reference()

    assert reference is not None
    _, metadata = reference
    assert metadata.edition_label is None
    assert metadata.captured_at is None
