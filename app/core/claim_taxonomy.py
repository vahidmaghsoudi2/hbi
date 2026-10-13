"""Compatibility import; canonical claim taxonomy lives in app.domain."""
from app.domain.claim_taxonomy import CLAIM_TYPES

__all__ = ["CLAIM_TYPES"]
