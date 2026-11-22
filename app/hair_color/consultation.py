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


def run_consultation_persian(request: Mapping[str, Any]) -> dict[str, Any]:
    """Convenience API for UI callers: raw validated result plus Persian rendering."""
    from .persian_response_renderer import render_persian_response
    from .publication_gate import evaluate_publication_gate

    result = run_consultation(request)
    gate = evaluate_publication_gate(
        result,
        current_case_version=request["case_version"],
        current_target_version=request["target_version"],
    )
    return {
        "consultation": result,
        "publication_gate": gate,
        "presentation": render_persian_response(gate["safe_response"]),
        "execution_authorized": False,
    }
