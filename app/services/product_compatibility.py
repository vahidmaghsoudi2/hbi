"""GAP-05 L1 controlled ProductKnowledge compatibility surface.

`ProductKnowledge.known_use_cases` is the approved product-side semantic surface.
Values are normalized deterministically to canonical Need ids using an explicit,
reviewable product-side vocabulary. Unknown product phrases are never guessed.
"""
from __future__ import annotations

from typing import List, Tuple

from app.services.need_normalization import CANONICAL_NEEDS

# Product-side vocabulary is intentionally separate from customer Need
# normalization. A phrase must be explicitly approved here before a product
# use-case can contribute to compatibility.
_PRODUCT_PHRASE_TO_CANONICAL = {
    "hydration": ("hydration",),
    "hydrate": ("hydration",),
    "hydrating": ("hydration",),
    "moisturize": ("hydration",),
    "moisturising": ("hydration",),
    "moisturizing": ("hydration",),
    "moisturizer": ("hydration",),
    "moisture": ("hydration",),
    "آبرسان": ("hydration",),
    "آبرسانی": ("hydration",),
    "مرطوب": ("hydration",),
    "مرطوب کننده": ("hydration",),
    "مرطوب‌کننده": ("hydration",),
    "barrier repair": ("barrier_repair",),
    "skin barrier": ("barrier_repair",),
    "سد پوستی": ("barrier_repair",),
    "ترمیم سد": ("barrier_repair",),
    "ترمیم سد پوستی": ("barrier_repair",),
    "dry skin": ("dry_skin",),
    "dryness": ("dry_skin",),
    "dehydrated": ("dry_skin",),
    "flaky": ("dry_skin",),
    "پوست خشک": ("dry_skin",),
    "خشکی": ("dry_skin",),
    "خشکی پوست": ("dry_skin",),
    "oily": ("oil_control",),
    "oily skin": ("oil_control",),
    "oil control": ("oil_control",),
    "sebum": ("oil_control",),
    "چرب": ("oil_control",),
    "پوست چرب": ("oil_control",),
    "کنترل چربی": ("oil_control",),
    "acne": ("acne_care",),
    "acne care": ("acne_care",),
    "pimple": ("acne_care",),
    "breakout": ("acne_care",),
    "جوش": ("acne_care",),
    "آکنه": ("acne_care",),
    "sensitive": ("sensitivity",),
    "sensitivity": ("sensitivity",),
    "irritated": ("sensitivity",),
    "حساس": ("sensitivity",),
    "پوست حساس": ("sensitivity",),
    "حساسیت": ("sensitivity",),
    "sunscreen": ("sun_protection",),
    "sun protection": ("sun_protection",),
    "spf": ("sun_protection",),
    "uv": ("sun_protection",),
    "ضدآفتاب": ("sun_protection",),
    "ضد آفتاب": ("sun_protection",),
    "محافظت در برابر آفتاب": ("sun_protection",),
    "brightening": ("brightening",),
    "pigmentation": ("brightening",),
    "dark spots": ("brightening",),
    "لک": ("brightening",),
    "روشن کننده": ("brightening",),
    "روشن‌کننده": ("brightening",),
    "anti aging": ("anti_aging",),
    "anti-aging": ("anti_aging",),
    "wrinkle": ("anti_aging",),
    "ضد چروک": ("anti_aging",),
    "ضدپیری": ("anti_aging",),
    "cleanse": ("cleansing",),
    "cleanser": ("cleansing",),
    "cleansing": ("cleansing",),
    "پاکسازی": ("cleansing",),
    "شوینده": ("cleansing",),
    # Explicit MVP seed compound/category phrases.
    "ضدآفتاب ضدلک صورت": ("sun_protection", "brightening"),
    "ضدآفتاب رنگی ضدلک صورت": ("sun_protection", "brightening"),
    "ضدآفتاب روزانه صورت": ("sun_protection",),
    "کرم روزانه ضدپیری صورت": ("anti_aging",),
}


def _normalize_product_phrase(text: str) -> str:
    key = (text or "").strip().lower().replace("\u200c", "")
    key = " ".join(key.split())
    return key.replace("-", " ").replace("_", " ")


def normalize_product_use_cases(known_use_cases: str | None) -> Tuple[List[str], List[str]]:
    """Normalize controlled ProductKnowledge use cases to canonical Need ids.

    Returns `(canonical_ids, unmapped_phrases)`. Matching is canonical-to-
    canonical. Product-side recognition never falls back to customer-side
    normalization, so an unapproved product phrase remains unmapped.
    """
    if not known_use_cases:
        return [], []

    canonical_ids: List[str] = []
    unmapped: List[str] = []
    seen = set()

    for raw in str(known_use_cases).replace(";", ",").replace("\n", ",").split(","):
        phrase = raw.strip()
        if not phrase:
            continue

        ids = _PRODUCT_PHRASE_TO_CANONICAL.get(_normalize_product_phrase(phrase), ())
        if not ids:
            unmapped.append(phrase)
            continue

        for cid in ids:
            if cid not in CANONICAL_NEEDS:
                unmapped.append(phrase)
                continue
            if cid not in seen:
                seen.add(cid)
                canonical_ids.append(cid)

    return canonical_ids, unmapped


def product_compatibility_ids(known_use_cases: str | None) -> List[str]:
    """Return only explicitly recognized canonical product compatibility ids."""
    ids, _ = normalize_product_use_cases(known_use_cases)
    return ids
