"""Registry of explicit owner-defined hair-color catalog rules.

These rules are policy/identity constraints only. They do not infer chemistry,
formula, lift, oxidation, or performance. Preserve source strings verbatim.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OwnerDefinedRule:
    rule_id: str
    title: str
    statement: str
    scope: str
    status: str = "owner_approved"
    limitation: str = "No chemical or performance claim is implied."


OWNER_DEFINED_RULES: tuple[OwnerDefinedRule, ...] = (
    OwnerDefinedRule(
        "OR-01",
        "Natural Extra comparative rule",
        "Natural Extra is stronger than its corresponding Natural Simple shade.",
        "Only explicitly corresponding Natural/Natural Extra shades; owner-defined comparison.",
        limitation=(
            "The word stronger is owner-defined and must not be interpreted as lift, "
            "oxidative strength, coverage, formula, or chemical performance."
        ),
    ),
    OwnerDefinedRule(
        "OR-02",
        "Numbering exceptions",
        "Codes 6.7, 8.56, 6.53, and 6.54 are exceptions to ordinary code interpretation.",
        "Only the four exact raw shade-code strings; requires special determination.",
        limitation="Do not decode digits, infer tone/pigment, or apply ordinary numbering assumptions.",
    ),
    OwnerDefinedRule(
        "OR-03",
        "Raw shade-code identity",
        "Preserve the original raw shade code exactly; never rewrite it as identity.",
        "All catalog shade-code strings and catalog identity handling.",
        limitation="Structural aliases may support comparison only; raw code remains source identity.",
    ),
    OwnerDefinedRule(
        "OR-04",
        "Natural Extra alias range",
        "Natural Extra aliases are limited to the explicitly approved +05 through +09 range.",
        "Natural Extra series only; exact explicitly documented aliases.",
        limitation="Do not extend the alias range, add undocumented spellings, or treat aliases as chemistry.",
    ),
    OwnerDefinedRule(
        "OR-05",
        "Rule scope and transfer",
        "An owner-defined rule applies only within its stated scope.",
        "Exact brand/series/code scope stated by each rule.",
        limitation="Do not generalize to other brands, series, or codes without explicit approved scope.",
    ),
    OwnerDefinedRule(
        "OR-06",
        "No chemical inference from owner rules",
        "Owner-defined catalog rules do not authorize chemical or service-performance claims.",
        "All owner-defined rules in this registry.",
        limitation="Formula, oxidation, lift, developer, ratio, processing time, safety, or outcome require separate evidence and specialist validation.",
    ),
)


def get_owner_defined_rule(rule_id: str) -> OwnerDefinedRule | None:
    """Return a rule only for an exact ID; unknown IDs fail closed."""
    if not isinstance(rule_id, str):
        return None
    return next((rule for rule in OWNER_DEFINED_RULES if rule.rule_id == rule_id), None)


def list_owner_defined_rule_ids() -> tuple[str, ...]:
    """Return stable registry IDs in declaration order."""
    return tuple(rule.rule_id for rule in OWNER_DEFINED_RULES)
