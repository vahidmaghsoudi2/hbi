"""Conservative Bijourka catalog family classification.

The raw series label is the catalog-native family identity. Editorial groupings
are proposed navigation buckets only; they are not PO-approved color theory,
chemistry, performance, or formula claims.
"""
from __future__ import annotations

from dataclasses import dataclass


# Exact series labels from the frozen 88-row catalog snapshot.
# Group labels are provisional navigation taxonomy, not source claims.
_SERIES_GROUPS = {
    "طبیعی": "natural",
    "طبیعی اکسترا": "natural",
    "خاکستری": "cool_named",
    "دودی": "cool_named",
    "زیتونی": "green_named",
    "طلایی": "gold_named",
    "بژ": "beige_named",
    "نسکافه ای": "brown_named",
    "آلبالویی": "red_named",
    "شکلاتی": "brown_named",
    "عسلی": "gold_named",
    "فندقی": "brown_named",
    "شرابی": "red_named",
    "قرمز": "red_named",
    "عروسکی": "creative_named",
    "بیسکویتی": "brown_named",
    "کاپوچینو": "brown_named",
    "ترکیبی": "creative_named",
    "واریاسیون": "special_named",
}


@dataclass(frozen=True)
class CatalogFamilyClassification:
    series_name_raw: str
    catalog_family_label: str
    editorial_group: str
    classification_source: str = "catalog_series_label"
    editorial_group_status: str = "provisional"


def classify_catalog_family(series_name_raw: object) -> CatalogFamilyClassification | None:
    """Classify only an exact raw series label; unknowns remain unclassified.

    catalog_family_label mirrors the raw series label. editorial_group is a
    provisional, explicitly non-technical grouping for navigation/filtering.
    """
    if not isinstance(series_name_raw, str) or series_name_raw not in _SERIES_GROUPS:
        return None
    return CatalogFamilyClassification(
        series_name_raw=series_name_raw,
        catalog_family_label=series_name_raw,
        editorial_group=_SERIES_GROUPS[series_name_raw],
    )


def known_catalog_family_labels() -> tuple[str, ...]:
    """Return the exact catalog family labels in the frozen snapshot."""
    return tuple(_SERIES_GROUPS)
