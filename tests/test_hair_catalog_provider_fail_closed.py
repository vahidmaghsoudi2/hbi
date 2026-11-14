from __future__ import annotations

import csv
import hashlib
import json

from app.domain import hair_catalog_provider as provider
from app.domain.hair_catalog_identity_lookup import CatalogIdentity


def _valid_csv(row_count: int = provider.EXPECTED_DATA_ROWS) -> str:
    headers = provider.EXPECTED_HEADERS
    lines = [",".join(headers)]
    for index in range(row_count):
        values = [
            f"Brand-{index}",
            f"Series-{index}",
            str(index + 1),
            f"Shade-{index}",
            "Synthetic specification",
            "Synthetic volume",
        ]
        lines.append(",".join(values))
    return "\n".join(lines) + "\n"


def _write_csv(tmp_path, content: str):
    path = tmp_path / "catalog.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_provider_fails_closed_when_catalog_has_wrong_row_count(tmp_path, monkeypatch):
    path = _write_csv(tmp_path, _valid_csv(row_count=provider.EXPECTED_DATA_ROWS - 1))
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_when_catalog_headers_are_changed(tmp_path, monkeypatch):
    headers = list(provider.EXPECTED_HEADERS)
    headers[2] = "شماره متفاوت"
    content = ",".join(headers) + "\n" + _valid_csv().split("\n", 1)[1]
    path = _write_csv(tmp_path, content)
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_when_required_identity_is_empty(tmp_path, monkeypatch):
    rows = list(csv.reader(_valid_csv().splitlines()))
    rows[1][3] = "   "
    from io import StringIO

    buffer = StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    path = _write_csv(tmp_path, buffer.getvalue())
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_on_duplicate_catalog_identity(tmp_path, monkeypatch):
    rows = list(csv.reader(_valid_csv().splitlines()))
    rows[2][:4] = rows[1][:4]
    from io import StringIO

    buffer = StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    path = _write_csv(tmp_path, buffer.getvalue())
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_on_invalid_utf8(tmp_path, monkeypatch):
    path = tmp_path / "catalog.csv"
    path.write_bytes(b"\xff\xfe\x00")
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_when_catalog_file_is_missing(tmp_path, monkeypatch):
    path = tmp_path / "missing.csv"
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.load_approved_hair_catalog_reference() is None



def test_provider_accepts_only_exact_identity_present_in_approved_csv(tmp_path, monkeypatch):
    path = _write_csv(tmp_path, _valid_csv())
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert provider.approved_catalog_contains_identity(
        CatalogIdentity(
            brand="Brand-0",
            series="Series-0",
            shade_number="1",
            shade_name="Shade-0",
        )
    )


def test_provider_rejects_identity_not_present_in_approved_csv(tmp_path, monkeypatch):
    path = _write_csv(tmp_path, _valid_csv())
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert not provider.approved_catalog_contains_identity(
        CatalogIdentity(
            brand="brand-0",
            series="Series-0",
            shade_number="1",
            shade_name="Shade-0",
        )
    )


def test_provider_rejects_identity_when_catalog_is_invalid(tmp_path, monkeypatch):
    path = _write_csv(tmp_path, _valid_csv(row_count=provider.EXPECTED_DATA_ROWS - 1))
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert not provider.approved_catalog_contains_identity(
        CatalogIdentity(
            brand="Brand-0",
            series="Series-0",
            shade_number="1",
            shade_name="Shade-0",
        )
    )



def test_provider_rejects_identity_when_reference_hash_differs(tmp_path, monkeypatch):
    path = _write_csv(tmp_path, _valid_csv())
    monkeypatch.setattr(provider, "_catalog_path", lambda: path)

    assert not provider.approved_catalog_contains_identity(
        CatalogIdentity(
            brand="Brand-0",
            series="Series-0",
            shade_number="1",
            shade_name="Shade-0",
        ),
        expected_content_sha256="0" * 64,
    )



def _write_manifest(tmp_path, catalog_path, **overrides):
    raw = catalog_path.read_bytes()
    manifest = {
        "schema_version": 1,
        "snapshot_id": "synthetic-hbi-snapshot-001",
        "ingestion_id": "synthetic-hbi-ingestion-001",
        "source_url": provider.REFERENCE_URL,
        "artifact_path": provider.CATALOG_RELATIVE_PATH.as_posix(),
        "snapshot_captured_at": "2026-11-10T18:57:00Z",
        "capture_method": "HBI_REPOSITORY_ARTIFACT_REGISTRATION",
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "publisher_edition": None,
        "publisher_revision": None,
        "publisher_captured_at": None,
        "validation_policy": "REVALIDATE_ON_EVERY_LOAD",
        "expected_row_count": provider.EXPECTED_DATA_ROWS,
        "expected_column_count": len(provider.EXPECTED_HEADERS),
    }
    manifest.update(overrides)
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_provider_loads_hbi_snapshot_metadata_without_inventing_publisher_edition(
    tmp_path, monkeypatch
):
    catalog_path = _write_csv(tmp_path, _valid_csv())
    manifest_path = _write_manifest(tmp_path, catalog_path)
    monkeypatch.setattr(provider, "_catalog_path", lambda: catalog_path)
    monkeypatch.setattr(provider, "_snapshot_manifest_path", lambda: manifest_path)

    loaded = provider.load_approved_hair_catalog_reference()

    assert loaded is not None
    reference_id, reference = loaded
    assert reference_id == "synthetic-hbi-snapshot-001"
    assert reference.snapshot_id == reference_id
    assert reference.ingestion_id == "synthetic-hbi-ingestion-001"
    assert reference.snapshot_captured_at == "2026-11-10T18:57:00Z"
    assert reference.snapshot_validation_status == "VALIDATED_ON_LOAD"
    assert reference.content_sha256 == hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    assert reference.edition_label is None
    assert reference.captured_at is None


def test_provider_fails_closed_when_snapshot_hash_does_not_match_catalog(
    tmp_path, monkeypatch
):
    catalog_path = _write_csv(tmp_path, _valid_csv())
    manifest_path = _write_manifest(tmp_path, catalog_path, content_sha256="0" * 64)
    monkeypatch.setattr(provider, "_catalog_path", lambda: catalog_path)
    monkeypatch.setattr(provider, "_snapshot_manifest_path", lambda: manifest_path)

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_when_snapshot_manifest_is_missing(tmp_path, monkeypatch):
    catalog_path = _write_csv(tmp_path, _valid_csv())
    monkeypatch.setattr(provider, "_catalog_path", lambda: catalog_path)
    monkeypatch.setattr(
        provider, "_snapshot_manifest_path", lambda: tmp_path / "missing.json"
    )

    assert provider.load_approved_hair_catalog_reference() is None


def test_provider_fails_closed_when_snapshot_timestamp_is_not_timezone_aware(
    tmp_path, monkeypatch
):
    catalog_path = _write_csv(tmp_path, _valid_csv())
    manifest_path = _write_manifest(
        tmp_path, catalog_path, snapshot_captured_at="2026-11-10T18:57:00"
    )
    monkeypatch.setattr(provider, "_catalog_path", lambda: catalog_path)
    monkeypatch.setattr(provider, "_snapshot_manifest_path", lambda: manifest_path)

    assert provider.load_approved_hair_catalog_reference() is None
