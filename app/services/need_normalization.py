"""
GAP-05 L1 — Controlled Semantic Need Normalization (deterministic, no LLM/embeddings).

Contract: docs/03_decision_log/HBI-PO-DEC-GAP05-001.md
- Canonical vocabulary + approved synonym/phrase mappings
- Auditable Factor → Need mapping
- Unmapped / ambiguous input is NOT silently guessed into a Need
- Scoring/weights unchanged; only Need surface fed to matching may change
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Surface forms are space-separated so frozen token-overlap matching remains
# compatible with typical ProductKnowledge.known_use_cases text.
CANONICAL_NEEDS = {
    "hydration": "hydration",
    "barrier_repair": "barrier repair",
    "dry_skin": "dry skin",
    "oil_control": "oil control",
    "acne_care": "acne care",
    "sensitivity": "sensitivity",
    "sun_protection": "sun protection",
    "brightening": "brightening",
    "anti_aging": "anti aging",
    "cleansing": "cleansing",
}

# Approved synonym / phrase → canonical Need id (lowercase match after light normalize).
# Only explicitly listed phrases map; everything else stays unmapped.
_SYNONYM_TO_CANONICAL: Dict[str, str] = {
    "hydration": "hydration",
    "hydrate": "hydration",
    "hydrating": "hydration",
    "moisturize": "hydration",
    "moisturising": "hydration",
    "moisturizing": "hydration",
    "moisturizer": "hydration",
    "moisture": "hydration",
    "آبرسان": "hydration",
    "آبرسانی": "hydration",
    "مرطوب": "hydration",
    "مرطوب کننده": "hydration",
    "مرطوب‌کننده": "hydration",
    "barrier": "barrier_repair",
    "barrier repair": "barrier_repair",
    "skin barrier": "barrier_repair",
    "repair barrier": "barrier_repair",
    "سد پوستی": "barrier_repair",
    "ترمیم سد": "barrier_repair",
    "ترمیم سد پوستی": "barrier_repair",
    "dry skin": "dry_skin",
    "dryness": "dry_skin",
    "dehydrated": "dry_skin",
    "flaky": "dry_skin",
    "پوست خشک": "dry_skin",
    "خشکی": "dry_skin",
    "خشکی پوست": "dry_skin",
    "پوسته پوسته": "dry_skin",
    "پوسته‌پوسته": "dry_skin",
    "oily": "oil_control",
    "oily skin": "oil_control",
    "oil control": "oil_control",
    "sebum": "oil_control",
    "چرب": "oil_control",
    "پوست چرب": "oil_control",
    "کنترل چربی": "oil_control",
    "acne": "acne_care",
    "acne care": "acne_care",
    "pimple": "acne_care",
    "breakout": "acne_care",
    "جوش": "acne_care",
    "آکنه": "acne_care",
    "sensitive": "sensitivity",
    "sensitivity": "sensitivity",
    "irritated": "sensitivity",
    "حساس": "sensitivity",
    "پوست حساس": "sensitivity",
    "حساسیت": "sensitivity",
    "sunscreen": "sun_protection",
    "sun protection": "sun_protection",
    "spf": "sun_protection",
    "uv": "sun_protection",
    "ضدآفتاب": "sun_protection",
    "ضد آفتاب": "sun_protection",
    "محافظت در برابر آفتاب": "sun_protection",
    "brightening": "brightening",
    "pigmentation": "brightening",
    "dark spots": "brightening",
    "لک": "brightening",
    "روشن کننده": "brightening",
    "روشن‌کننده": "brightening",
    "anti aging": "anti_aging",
    "anti-aging": "anti_aging",
    "wrinkle": "anti_aging",
    "ضد چروک": "anti_aging",
    "ضدپیری": "anti_aging",
    "cleanse": "cleansing",
    "cleanser": "cleansing",
    "cleansing": "cleansing",
    "پاکسازی": "cleansing",
    "شوینده": "cleansing",
}


def _light_normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = t.replace("\u200c", "")  # ZWNJ
    t = " ".join(t.split())
    return t


def map_phrase_to_canonical(phrase: str) -> Optional[str]:
    """Return canonical Need id if phrase is in the approved map; else None (no guessing)."""
    key = _light_normalize(phrase)
    if not key:
        return None
    if key in _SYNONYM_TO_CANONICAL:
        return _SYNONYM_TO_CANONICAL[key]
    key2 = key.replace("-", " ").replace("_", " ")
    key2 = " ".join(key2.split())
    return _SYNONYM_TO_CANONICAL.get(key2)


def normalize_needs_from_factors(
    factors: List[Dict[str, Any]],
) -> Tuple[List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Derive canonical Needs from Decision State factors.

    Returns:
      needs: ordered unique canonical Need surface strings
      mappings: audit trail {factor_value, canonical, rule}
      unmapped: factors that did not map (explicit, not invented)
    """
    needs: List[str] = []
    mappings: List[Dict[str, Any]] = []
    unmapped: List[Dict[str, Any]] = []
    seen = set()

    for f in factors or []:
        raw = (f.get("value") or "").strip()
        if not raw:
            continue
        canonical_id = map_phrase_to_canonical(raw)
        if canonical_id is None:
            unmapped.append({
                "factor_value": raw,
                "source": f.get("source"),
                "validity": f.get("validity"),
                "reason": "no_approved_mapping",
            })
            continue
        canonical_surface = CANONICAL_NEEDS[canonical_id]
        mappings.append({
            "factor_value": raw,
            "canonical": canonical_surface,
            "canonical_id": canonical_id,
            "source": f.get("source"),
            "validity": f.get("validity"),
            "rule": "approved_synonym_map",
        })
        if canonical_surface not in seen:
            seen.add(canonical_surface)
            needs.append(canonical_surface)

    return needs, mappings, unmapped
