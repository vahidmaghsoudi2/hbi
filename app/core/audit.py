"""Minimal structured security audit logging (stdlib only).

Emits JSON lines to the standard logger named 'hbi.audit'.
Does not replace application logging; only security-relevant events.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_audit_logger = logging.getLogger("hbi.audit")
if not _audit_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _audit_logger.addHandler(_handler)
    _audit_logger.setLevel(logging.INFO)
    _audit_logger.propagate = False


def audit_event(
    event: str,
    *,
    customer_id: Optional[str] = None,
    path: Optional[str] = None,
    outcome: str = "ok",
    detail: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    payload: Dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "outcome": outcome,
    }
    if customer_id:
        payload["customer_id"] = customer_id
    if path:
        payload["path"] = path
    if detail:
        payload["detail"] = detail
    if extra:
        payload.update(extra)
    _audit_logger.info(json.dumps(payload, ensure_ascii=False))
