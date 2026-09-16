"""GAP-05 L1 ProductKnowledge compatibility acceptance tests."""

from app.services.product_compatibility import normalize_product_use_cases
from app.services.recommendation_service import RecommendationService


def test_product_use_case_exact_synonyms_normalize_to_canonical_ids():
    ids, unmapped = normalize_product_use_cases("آبرسانی, ضدآفتاب, ضدپیری")
    assert ids == ["hydration", "sun_protection", "anti_aging"]
    assert unmapped == []


def test_existing_seed_category_phrases_are_explicitly_controlled():
    ids, unmapped = normalize_product_use_cases("ضدآفتاب ضدلک صورت")
    assert ids == ["sun_protection", "brightening"]
    assert unmapped == []


def test_unknown_product_use_case_is_not_guessed():
    ids, unmapped = normalize_product_use_cases("کاربرد ناشناخته محصول")
    assert ids == []
    assert unmapped == ["کاربرد ناشناخته محصول"]


def test_product_surface_does_not_fall_back_to_customer_vocabulary():
    # This phrase exists in the customer-side Need vocabulary but is not
    # independently approved in the product-side vocabulary.
    ids, unmapped = normalize_product_use_cases("پوسته‌پوسته")
    assert ids == []
    assert unmapped == ["پوسته‌پوسته"]


def test_matching_is_canonical_to_canonical_not_raw_token_overlap():
    svc = RecommendationService.__new__(RecommendationService)
    assert svc._calculate_need_match(["hydration"], "آبرسانی") == 1.0
    assert svc._calculate_need_match(["hydration"], "moisturizing face") == 0.0
    assert svc._calculate_need_match(["hydration"], "hydration moisturizing face") == 0.0
    assert svc._calculate_need_match(["hydration"], "unrelated product text") == 0.0


def test_compound_product_surface_matches_multiple_canonical_needs():
    svc = RecommendationService.__new__(RecommendationService)
    score = svc._calculate_need_match(
        ["sun protection", "brightening"],
        "ضدآفتاب ضدلک صورت",
    )
    assert score == 1.0


def test_frozen_need_match_formula_is_preserved():
    svc = RecommendationService.__new__(RecommendationService)
    # One of two generated Needs is explicitly compatible → 0.5.
    assert svc._calculate_need_match(
        ["hydration", "dry skin"],
        "hydration",
    ) == 0.5
