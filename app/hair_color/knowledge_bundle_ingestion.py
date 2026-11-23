"""Safe, non-activating import boundary for inactive evidence bundles.

Accepts a JSON string or mapping, validates schema/version and provenance, and
returns only metadata. This module has no persistence, activation, or publication
capability.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .knowledge_bundle_provenance import validate_knowledge_bundle, KnowledgeBundleValidationError

SUPPORTED_SCHEMA_VERSION = "1.0"


class KnowledgeBundleImportError(ValueError):
    """Raised when an import payload cannot be parsed or supported."""


def ingest_knowledge_bundle(payload: str | Mapping[str, Any]) -> dict[str, Any]:
    """Parse and validate an evidence bundle, keeping it inactive."""
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise KnowledgeBundleImportError("payload is not valid JSON") from exc
    elif isinstance(payload, Mapping):
        parsed = dict(payload)
    else:
        raise KnowledgeBundleImportError("payload must be JSON text or an object")

    if not isinstance(parsed, Mapping):
        raise KnowledgeBundleImportError("bundle envelope must be an object")
    schema_version = parsed.get("bundle_schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise KnowledgeBundleImportError("unsupported bundle_schema_version")

    bundle = parsed.get("bundle")
    try:
        validation = validate_knowledge_bundle(bundle)
    except KnowledgeBundleValidationError as exc:
        raise KnowledgeBundleImportError(f"bundle provenance validation failed: {exc}") from exc

    return {
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "imported": True,
        "metadata_valid": validation["metadata_valid"],
        "bundle_ref": validation["bundle_ref"],
        "product_identity": validation["product_identity"],
        "source_count": validation["source_count"],
        "claim_count": validation["claim_count"],
        "specialist_approval_record_valid": validation["specialist_approval_record_valid"],
        "status": "INACTIVE_REVIEW_REQUIRED",
        "publishable": False,
        "activation_allowed": False,
        "limitations": validation["limitations"] + [
            "Import is in-memory metadata validation only; no persistence, activation, or publication occurs."
        ],
    }
