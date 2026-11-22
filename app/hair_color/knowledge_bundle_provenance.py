"""Evidence/provenance metadata validator for inactive synthetic knowledge bundles.

This infrastructure checks metadata completeness and link integrity only. It does
not assess scientific correctness, product chemistry, safety, or suitability.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class KnowledgeBundleValidationError(ValueError):
    """Raised when provenance metadata is incomplete or internally inconsistent."""


_REQUIRED_PRODUCT = ("product_id", "brand", "market", "product_version")
_REQUIRED_SOURCE = ("source_id", "publisher", "title", "source_version", "applicability")
_REQUIRED_CLAIM = ("claim_id", "claim_text", "source_refs")


def validate_knowledge_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate structure and traceability; never activates or publishes a bundle."""
    if not isinstance(bundle, Mapping):
        raise KnowledgeBundleValidationError("bundle must be a mapping")
    product = bundle.get("product_identity")
    if not isinstance(product, Mapping):
        raise KnowledgeBundleValidationError("product_identity is required")
    for key in _REQUIRED_PRODUCT:
        if not isinstance(product.get(key), str) or not product[key].strip():
            raise KnowledgeBundleValidationError(f"product_identity.{key} is required")

    sources = bundle.get("sources")
    if not isinstance(sources, list) or not sources:
        raise KnowledgeBundleValidationError("at least one source record is required")
    source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, Mapping):
            raise KnowledgeBundleValidationError("source records must be objects")
        for key in _REQUIRED_SOURCE:
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise KnowledgeBundleValidationError(f"source.{key} is required")
        if source["source_id"] in source_ids:
            raise KnowledgeBundleValidationError("source_id values must be unique")
        source_ids.add(source["source_id"])

    claims = bundle.get("claims")
    if not isinstance(claims, list) or not claims:
        raise KnowledgeBundleValidationError("at least one claim record is required")
    claim_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, Mapping):
            raise KnowledgeBundleValidationError("claim records must be objects")
        for key in _REQUIRED_CLAIM:
            if key == "source_refs":
                continue
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                raise KnowledgeBundleValidationError(f"claim.{key} is required")
        if claim["claim_id"] in claim_ids:
            raise KnowledgeBundleValidationError("claim_id values must be unique")
        claim_ids.add(claim["claim_id"])
        refs = claim.get("source_refs")
        if not isinstance(refs, list) or not refs or any(
            not isinstance(ref, str) or not ref.strip() for ref in refs
        ):
            raise KnowledgeBundleValidationError("claim.source_refs must be non-empty strings")
        if len(refs) != len(set(refs)):
            raise KnowledgeBundleValidationError("claim.source_refs must not contain duplicates")
        if any(ref not in source_ids for ref in refs):
            raise KnowledgeBundleValidationError("claim references unknown source_id")

    approval = bundle.get("specialist_approval")
    approved = isinstance(approval, Mapping) and (
        approval.get("status") == "APPROVED"
        and isinstance(approval.get("approved_by"), str)
        and bool(approval["approved_by"].strip())
        and isinstance(approval.get("approved_at"), str)
        and bool(approval["approved_at"].strip())
        and isinstance(approval.get("scope"), str)
        and bool(approval["scope"].strip())
    )
    return {
        "bundle_ref": bundle.get("bundle_ref"),
        "product_identity": dict(product),
        "source_count": len(sources),
        "claim_count": len(claims),
        "metadata_valid": True,
        "specialist_approval_record_valid": bool(approved),
        "publishable": False,
        "activation_allowed": False,
        "status": "APPROVAL_METADATA_RECORDED" if approved else "READY_FOR_SPECIALIST_REVIEW",
        "limitations": [
            "Structural/provenance validation only; scientific validity is not assessed.",
            "This validator never activates or publishes knowledge.",
        ],
    }
