"""Compatibility import; canonical claim taxonomy lives in app.domain."""
from app.domain.claim_taxonomy import ALLOWED_CLAIM_TYPES, CLAIM_TYPES, normalize_claim_type_value

__all__ = ["ALLOWED_CLAIM_TYPES", "CLAIM_TYPES", "normalize_claim_type_value"]
