"""Public entry point for the currently supported Hair Color consultation.

This callable is intentionally a policy/intake gate, not a recommendation
engine. The specialist knowledge bundle remains unavailable/unapproved.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .adapter import HairColorAdapter
from .policy_gate_engine import PolicyGateEngine


_POLICY_GATE_ADAPTER = HairColorAdapter(PolicyGateEngine())


def run_consultation(request: Mapping[str, Any]) -> dict[str, Any]:
    """Run a fail-closed intake/triage consultation; no color candidates are emitted."""
    return _POLICY_GATE_ADAPTER.evaluate(request)
