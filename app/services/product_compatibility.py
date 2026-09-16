"""GAP-05 L1 controlled ProductKnowledge compatibility surface.

`ProductKnowledge.known_use_cases` is the approved product-side semantic surface.
Values are normalized deterministically to canonical Need ids using an explicit,
reviewable vocabulary. Unknown product phrases are never guessed.
"""
from __future__ import annotations

from typing import List, Tuple

from app.services.need_normalization import CANONICAL_NEEDS, map_phrase_to_canonical

# Explicit product-side compound/category phrases already present in the MVP
# seed records. Each phrase is an auditable declaration of one or more canonical
# product use cases; it is not inferred from arbitrary token overlap.
_PRODUCT_PHRASE_TO_CANONICAL = {
    "ضدآفتاب ضدلک صورت": ("sun_protection", "brightening"),
    "ضدآفتاب رنگی ضدلک صورت": ("sun_protection", "brightening"),
    "ضدآفتاب روزانه صورت": ("sun_protection",),
    "کرم روزانه ضدپیری صورت": ("anti_aging",),
}


def normalize_product_use_cases(known_use_cases: str | None) -> Tuple[List[str], List[str]]:
    """Normalize controlled ProductKnowledge use cases to canonical Need ids.

    Returns `(canonical_ids, unmapped_phrases)`. The field is treated as a
    controlled semantic surface, so matching is canonical-to-canonical rather
    than raw token overlap. Comma/semicolon/newline delimiters allow multiple
    independently declared use cases.
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

        ids = _PRODUCT_PHRASE_TO_CANONICAL.get(phrase)
        if ids is None:
            cid = map_phrase_to_canonical(phrase)
            ids = (cid,) if cid else ()

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
