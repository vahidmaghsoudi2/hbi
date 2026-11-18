"""Conservative structural rules for raw Bijourka shade-number strings.

This module classifies notation and applies only explicitly owner-defined
numbering relations. It does not infer tone, pigment, chemistry, lift, formula,
developer, processing time, or expected color performance.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


_DIGITS = "0-9۰-۹"
_INTEGER = re.compile(rf"^[{_DIGITS}]+$")
_PLUS_INTEGER = re.compile(rf"^\+[{_DIGITS}]+$")
_DECIMAL = re.compile(rf"^[{_DIGITS}]+(?:\.[{_DIGITS}]+)+$")
_ALPHA_DECIMAL = re.compile(r"^[A-Za-z]+\.[0-9]+$")

# These are explicit notation relations only. The source string is never
# rewritten in catalog identity or persistence.
_EXTRA_ALIAS = {
    "+۰۵": "۵.۰۰",
    "+۰۶": "۶.۰۰",
    "+۰۷": "۷.۰۰",
    "+۰۸": "۸.۰۰",
    "+۰۹": "۹.۰۰",
    "+05": "5.00",
    "+06": "6.00",
    "+07": "7.00",
    "+08": "8.00",
    "+09": "9.00",
}

# Owner-defined exceptions: retain as opaque exceptional codes. No semantic
# decoding is authorized by this list.
OWNER_EXCEPTION_CODES = frozenset(
    {"۶.۷", "۸.۵۶", "۶.۵۳", "۶.۵۴", "6.7", "8.56", "6.53", "6.54"}
)
NATURAL_SIMPLE_CODES = frozenset(str(n) for n in range(1, 11)) | frozenset(
    "۰۱۲۳۴۵۶۷۸۹"
)
NATURAL_EXTRA_CODES = frozenset({f"+۰{n}" for n in range(5, 10)}) | frozenset(
    {f"+0{n}" for n in range(5, 10)}
)


@dataclass(frozen=True)
class NumberingAnalysis:
    raw_code: str
    notation: str
    recognized: bool
    structural_alias: str | None
    is_owner_exception: bool


def analyze_shade_code(raw_code: str) -> NumberingAnalysis:
    """Classify notation without changing or numerically interpreting raw_code."""
    if not isinstance(raw_code, str) or not raw_code:
        return NumberingAnalysis(str(raw_code), "invalid", False, None, False)

    if raw_code != raw_code.strip():
        return NumberingAnalysis(raw_code, "invalid", False, None, False)

    if raw_code in _EXTRA_ALIAS:
        notation = "plus_integer"
    elif _INTEGER.fullmatch(raw_code):
        notation = "integer"
    elif _PLUS_INTEGER.fullmatch(raw_code):
        notation = "plus_integer"
    elif _DECIMAL.fullmatch(raw_code):
        notation = "decimal"
    elif _ALPHA_DECIMAL.fullmatch(raw_code):
        notation = "alpha_decimal"
    else:
        notation = "unrecognized"

    return NumberingAnalysis(
        raw_code=raw_code,
        notation=notation,
        recognized=notation != "unrecognized",
        structural_alias=_EXTRA_ALIAS.get(raw_code),
        is_owner_exception=raw_code in OWNER_EXCEPTION_CODES,
    )


def validate_owner_defined_series_range(series_name_raw: str, shade_code_raw: str) -> bool | None:
    """Validate only the two explicitly bounded natural-series code families.

    True/False is returned for the two named series. None means this module
    has no approved range rule for that series and makes no range assertion.
    """
    if series_name_raw == "طبیعی":
        return shade_code_raw in NATURAL_SIMPLE_CODES
    if series_name_raw == "طبیعی اکسترا":
        return shade_code_raw in NATURAL_EXTRA_CODES
    return None


def natural_extra_is_owner_defined_stronger_than_natural_simple() -> bool:
    """Return the approved qualitative owner rule; it is not a chemistry claim."""
    return True
