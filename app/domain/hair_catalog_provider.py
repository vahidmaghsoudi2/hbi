"""Read-only server-side provider for the PO-approved 88-row hair catalog.

The CSV is treated as a catalog identity artifact only. It is not evidence of
chemical composition, safety, suitability, or an expected result. The source
edition and capture timestamp are intentionally left unset: the artifact is
not versioned, so downstream lookup must remain inconclusive/fail-closed.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from app.domain.hair_catalog_identity_lookup import CatalogReference


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
        rows = list(csv.DictReader(text.splitlines()))
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
