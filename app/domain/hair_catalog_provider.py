"""Read-only server-side provider for the PO-approved 88-row hair catalog.

The CSV is a catalog identity artifact only. It is not evidence of chemical
composition, safety, suitability, or an expected result. Publisher edition
and source-capture provenance remain unset until independently established.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from io import StringIO
from pathlib import Path

from app.domain.hair_catalog_identity_lookup import CatalogIdentity, CatalogReference


CATALOG_RELATIVE_PATH = Path(
    "docs/homepage/encyclopedia/hair-color/catalog/raeaka_bijourka_catalog.csv"
)
SNAPSHOT_MANIFEST_RELATIVE_PATH = Path(
    "docs/homepage/encyclopedia/hair-color/catalog/raeaka_bijourka_snapshot.json"
)
EXPECTED_DATA_ROWS = 88
EXPECTED_HEADERS = (
    "برند",
    "سری محصول",
    "شماره رنگ",
    "نام رنگ",
    "مشخصات قلم محصول",
    "حجم محصول",
)
IDENTITY_COLUMNS = ("برند", "سری محصول", "شماره رنگ", "نام رنگ")
REFERENCE_URL = "https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/"


def _catalog_path() -> Path:
    repository_root = Path(__file__).resolve().parents[2]
    return repository_root / CATALOG_RELATIVE_PATH


def _snapshot_manifest_path() -> Path:
    repository_root = Path(__file__).resolve().parents[2]
    return repository_root / SNAPSHOT_MANIFEST_RELATIVE_PATH


def _valid_aware_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _read_validated_snapshot_manifest(content_sha256: str) -> dict[str, object] | None:
    """Load HBI-owned snapshot metadata and bind it to the exact CSV bytes.

    Publisher edition/revision and publisher capture time remain separate,
    nullable fields. HBI capture time never fills those publisher fields.
    """
    try:
        manifest = json.loads(_snapshot_manifest_path().read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(manifest, dict):
        return None
    required_strings = ("snapshot_id", "ingestion_id", "source_url", "artifact_path")
    if any(not isinstance(manifest.get(key), str) or not manifest[key].strip()
           for key in required_strings):
        return None
    if manifest.get("schema_version") != 1:
        return None
    if manifest.get("source_url") != REFERENCE_URL:
        return None
    if manifest.get("artifact_path") != CATALOG_RELATIVE_PATH.as_posix():
        return None
    if manifest.get("content_sha256") != content_sha256:
        return None
    if not _valid_aware_timestamp(manifest.get("snapshot_captured_at")):
        return None
    if manifest.get("capture_method") != "HBI_REPOSITORY_ARTIFACT_REGISTRATION":
        return None
    if manifest.get("validation_policy") != "REVALIDATE_ON_EVERY_LOAD":
        return None
    if manifest.get("expected_row_count") != EXPECTED_DATA_ROWS:
        return None
    if manifest.get("expected_column_count") != len(EXPECTED_HEADERS):
        return None

    publisher_edition = manifest.get("publisher_edition")
    publisher_revision = manifest.get("publisher_revision")
    publisher_captured_at = manifest.get("publisher_captured_at")
    for value in (publisher_edition, publisher_revision):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            return None
    if publisher_captured_at is not None and not _valid_aware_timestamp(publisher_captured_at):
        return None
    return manifest


def _read_validated_catalog() -> tuple[bytes, list[dict[str, str]]] | None:
    """Read one byte snapshot and validate its shape and identity uniqueness."""
    try:
        raw = _catalog_path().read_bytes()
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(StringIO(text, newline="")))
    except (OSError, UnicodeDecodeError, csv.Error):
        return None

    if len(rows) != EXPECTED_DATA_ROWS:
        return None
    if tuple(rows[0].keys()) != EXPECTED_HEADERS:
        return None
    if any(tuple(row.keys()) != EXPECTED_HEADERS for row in rows):
        return None

    seen: set[tuple[str, ...]] = set()
    for row in rows:
        if any(
            not isinstance(row.get(column), str) or not row[column].strip()
            for column in IDENTITY_COLUMNS
        ):
            return None
        identity = tuple(row[column] for column in IDENTITY_COLUMNS)
        if identity in seen:
            return None
        seen.add(identity)

    return raw, rows


def approved_catalog_contains_identity(
    identity: CatalogIdentity,
    *,
    expected_content_sha256: str | None = None,
) -> bool:
    """Return True only for an exact identity in the validated server CSV.

    No normalization, aliases, fuzzy matching, or caller-provided source
    metadata are accepted. When supplied, the expected hash binds this
    membership check to the exact reference snapshot already loaded by API.
    """
    if not isinstance(identity, CatalogIdentity):
        return False

    snapshot = _read_validated_catalog()
    if snapshot is None:
        return False
    raw, rows = snapshot

    digest = hashlib.sha256(raw).hexdigest()
    if expected_content_sha256 is not None and digest != expected_content_sha256:
        return False

    values = (
        identity.brand,
        identity.series,
        identity.shade_number,
        identity.shade_name,
    )
    if any(not isinstance(value, str) or not value.strip() for value in values):
        return False

    identities = {
        tuple(row[column] for column in IDENTITY_COLUMNS)
        for row in rows
    }
    return values in identities


def load_approved_hair_catalog_reference() -> tuple[str, CatalogReference] | None:
    """Load the validated server-owned CSV reference without inventing a version.

    The SHA-256 identifies the exact bytes. It does not substitute for a
    publisher-issued edition/revision or a separately evidenced capture time.
    """
    snapshot = _read_validated_catalog()
    if snapshot is None:
        return None
    raw, _ = snapshot

    digest = hashlib.sha256(raw).hexdigest()
    manifest = _read_validated_snapshot_manifest(digest)
    if manifest is None:
        return None

    reference_id = str(manifest["snapshot_id"])
    reference = CatalogReference(
        source_kind="RAEAKA_BIJOURKA_CATALOG",
        approval_status="PO_APPROVED",
        url=REFERENCE_URL,
        edition_label=manifest.get("publisher_edition"),
        captured_at=manifest.get("publisher_captured_at"),
        content_sha256=digest,
        snapshot_id=str(manifest["snapshot_id"]),
        snapshot_captured_at=str(manifest["snapshot_captured_at"]),
        ingestion_id=str(manifest["ingestion_id"]),
        snapshot_validation_status="VALIDATED_ON_LOAD",
    )
    return reference_id, reference
