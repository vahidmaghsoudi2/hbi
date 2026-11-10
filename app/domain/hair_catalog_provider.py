"""Read-only server-side provider for the PO-approved 88-row hair catalog.

The CSV is treated as a catalog identity artifact only. It is not evidence of
chemical composition, safety, suitability, or an expected result. The source
edition and capture timestamp are intentionally left unset: the artifact is
not versioned, so downstream lookup must remain inconclusive/fail-closed.
"""
from __future__ import annotations

import csv
import hashlib
from io import StringIO
from pathlib import Path

from app.domain.hair_catalog_identity_lookup import CatalogIdentity, CatalogReference


CATALOG_RELATIVE_PATH = Path(
    "docs/homepage/encyclopedia/hair-color/catalog/raeaka_bijourka_catalog.csv"
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
REFERENCE_URL = "https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/"


class HairCatalogProviderError(RuntimeError):
    """Raised when the approved catalog artifact is missing or malformed."""


def _catalog_path() -> Path:
    repository_root = Path(__file__).resolve().parents[2]
    return repository_root / CATALOG_RELATIVE_PATH


def approved_catalog_contains_identity(
    identity: CatalogIdentity,
    *,
    expected_content_sha256: str | None = None,
) -> bool:
    """Return True only when all four identity fields exactly match a CSV row.

    No normalization, aliases, fuzzy matching, or caller-provided source
    metadata are accepted. Invalid/missing catalog data fails closed.
    """
    if not isinstance(identity, CatalogIdentity):
        return False
    path = _catalog_path()
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(StringIO(text, newline="")))
    except (OSError, UnicodeDecodeError, csv.Error):
        return False

    if expected_content_sha256 is not None:
        if hashlib.sha256(raw).hexdigest() != expected_content_sha256:
            return False
    if not rows or len(rows) != EXPECTED_DATA_ROWS:
        return False
    if tuple(rows[0].keys()) != EXPECTED_HEADERS:
        return False
    if any(tuple(row.keys()) != EXPECTED_HEADERS for row in rows):
        return False

    required = ("برند", "سری محصول", "شماره رنگ", "نام رنگ")
    values = (
        identity.brand,
        identity.series,
        identity.shade_number,
        identity.shade_name,
    )
    if any(not isinstance(value, str) or not value.strip() for value in values):
        return False

    seen: set[tuple[str, ...]] = set()
    for row in rows:
        if any(not isinstance(row.get(field), str) or not row[field].strip() for field in required):
            return False
        key = tuple(row[field] for field in required)
        if key in seen:
            return False
        seen.add(key)

    return values in seen


def load_approved_hair_catalog_reference() -> tuple[str, CatalogReference] | None:
    """Load and validate the server-owned CSV; never infer a version label.

    A missing or malformed artifact returns None so the API can fail closed.
    The content hash identifies the exact bytes currently loaded; it does not
    substitute for a publisher-issued edition or capture provenance.
    """
    path = _catalog_path()
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(StringIO(text, newline="")))
    except (OSError, UnicodeDecodeError, csv.Error):
        return None

    if not rows or len(rows) != EXPECTED_DATA_ROWS:
        return None
    if tuple(rows[0].keys()) != EXPECTED_HEADERS:
        return None
    if any(tuple(row.keys()) != EXPECTED_HEADERS for row in rows):
        return None

    required = ("برند", "سری محصول", "شماره رنگ", "نام رنگ")
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        if any(not isinstance(row.get(field), str) or not row[field].strip() for field in required):
            return None
        identity = tuple(row[field] for field in required)
        if identity in seen:
            return None
        seen.add(identity)

    digest = hashlib.sha256(raw).hexdigest()
    reference_id = f"raeaka-bijourka-csv-sha256-{digest}"
    reference = CatalogReference(
        source_kind="RAEAKA_BIJOURKA_CATALOG",
        approval_status="PO_APPROVED",
        url=REFERENCE_URL,
        edition_label=None,
        captured_at=None,
        content_sha256=digest,
    )
    return reference_id, reference
