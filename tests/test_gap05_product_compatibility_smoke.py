from app.services.product_compatibility import normalize_product_use_cases
from app.services.recommendation_service import RecommendationService


def test_controlled_product_surface_maps_canonically():
    ids, unmapped = normalize_product_use_cases("ضدآفتاب ضدلک صورت")
    assert ids == ["sun_protection", "brightening"]
    assert unmapped == []


def test_unknown_product_surface_is_not_guessed():
    ids, unmapped = normalize_product_use_cases("کاربرد نامشخص")
    assert ids == []
    assert unmapped == ["کاربرد نامشخص"]


def test_need_match_uses_canonical_compatibility():
    service = RecommendationService.__new__(RecommendationService)
    assert service._calculate_need_match(["hydration"], "آبرسانی") == 1.0
    assert service._calculate_need_match(["hydration"], "متن نامرتبط") == 0.0
    assert service._calculate_need_match(["sun protection", "brightening"], "ضدآفتاب ضدلک صورت") == 1.0
