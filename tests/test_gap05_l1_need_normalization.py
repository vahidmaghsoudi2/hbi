"""GAP-05 L1 — Controlled Semantic Need Normalization tests (contract acceptance)."""
from app.services.need_normalization import (
    map_phrase_to_canonical,
    normalize_needs_from_factors,
    classify_phrase,
    CANONICAL_NEEDS,
)
from app.services.recommendation_service import RecommendationService


def test_approved_synonyms_same_canonical():
    a = map_phrase_to_canonical("آبرسان")
    b = map_phrase_to_canonical("hydration")
    c = map_phrase_to_canonical("moisturize")
    assert a == b == c == "hydration"


def test_equivalent_phrase_variants():
    assert map_phrase_to_canonical("dry skin") == "dry_skin"
    assert map_phrase_to_canonical("پوست خشک") == "dry_skin"
    assert map_phrase_to_canonical("barrier repair") == "barrier_repair"


def test_unrelated_terms_do_not_guess():
    assert map_phrase_to_canonical("quantum foam") is None
    assert map_phrase_to_canonical("xyz_unknown_term") is None
    cid, reason = classify_phrase("quantum foam")
    assert cid is None and reason == "no_approved_mapping"


def test_unmapped_remains_explicit():
    factors = [
        {"name": "concern", "value": "آبرسان", "source": "customer_input", "validity": "DECLARED"},
        {"name": "concern", "value": "something_unmapped_zzz", "source": "customer_input", "validity": "DECLARED"},
    ]
    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(factors)
    assert needs == ["hydration"]
    assert len(mappings) == 1
    assert mappings[0]["canonical"] == "hydration"
    assert mappings[0]["rule"] == "approved_synonym_map"
    assert len(unmapped) == 1
    assert unmapped[0]["factor_value"] == "something_unmapped_zzz"
    assert unmapped[0]["reason"] == "no_approved_mapping"
    assert ambiguous == []


def test_materially_ambiguous_not_normalized():
    """Materially ambiguous phrases (partial / multi-concept token hits) stay uncertain."""
    factors = [
        {"value": "dry oily skin", "source": "customer_input", "validity": "DECLARED"},
        {"value": "حساس چرب", "source": "customer_input", "validity": "DECLARED"},
        {"value": "dryness and sebum", "source": "customer_input", "validity": "DECLARED"},
    ]
    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(factors)
    assert needs == []
    assert mappings == []
    assert unmapped == []
    assert len(ambiguous) == 3
    for a in ambiguous:
        assert a["reason"] == "ambiguous"
        assert a["status"] == "uncertain"
        assert a["source"] == "customer_input"
        assert a["validity"] == "DECLARED"
    cid, reason = classify_phrase("dry oily skin")
    assert cid is None and reason == "ambiguous"


def test_partial_single_token_is_ambiguous_not_guessed():
    """A token that exists in the map but the full phrase is not approved → ambiguous."""
    cid, reason = classify_phrase("oily unknown")
    assert cid is None and reason == "ambiguous"
    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(
        [{"value": "oily unknown", "source": "s", "validity": "DECLARED"}]
    )
    assert needs == [] and mappings == [] and unmapped == []
    assert len(ambiguous) == 1 and ambiguous[0]["reason"] == "ambiguous"


def test_determinism():
    factors = [
        {"value": "sunscreen"},
        {"value": "ضدآفتاب"},
        {"value": "spf"},
    ]
    n1, m1, u1, a1 = normalize_needs_from_factors(factors)
    n2, m2, u2, a2 = normalize_needs_from_factors(factors)
    assert n1 == n2 == ["sun protection"]
    assert len(m1) == len(m2) == 3
    assert u1 == u2 == []
    assert a1 == a2 == []


def test_traceability_factor_to_need():
    factors = [{"value": "acne", "source": "customer_input", "validity": "DECLARED"}]
    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(factors)
    assert needs == ["acne care"]
    assert mappings[0]["factor_value"] == "acne"
    assert mappings[0]["source"] == "customer_input"
    assert mappings[0]["validity"] == "DECLARED"
    assert unmapped == []
    assert ambiguous == []


def test_decision_state_path_sets_audit_fields():
    svc = RecommendationService.__new__(RecommendationService)
    ds = {
        "factors": [
            {"value": "hydration", "source": "customer_input", "validity": "DECLARED"},
            {"value": "not_in_map_abc", "source": "customer_input", "validity": "DECLARED"},
            {"value": "dry oily", "source": "customer_input", "validity": "DECLARED"},
        ],
        "decision_status": "READY",
    }
    needs = svc._generate_needs_from_decision_state(ds)
    assert needs == ["hydration"]
    assert ds["need_mappings"][0]["canonical"] == "hydration"
    assert ds["unmapped_need_factors"][0]["factor_value"] == "not_in_map_abc"
    assert ds["ambiguous_need_factors"][0]["factor_value"] == "dry oily"
    assert ds["ambiguous_need_factors"][0]["reason"] == "ambiguous"
    assert ds["ambiguous_need_factors"][0]["status"] == "uncertain"


def test_only_unmapped_or_ambiguous_marks_insufficient():
    svc = RecommendationService.__new__(RecommendationService)
    ds = {
        "factors": [{"value": "totally_unknown_phrase_qqq", "source": "customer_input", "validity": "DECLARED"}],
        "decision_status": "READY",
    }
    needs = svc._generate_needs_from_decision_state(ds)
    assert needs == []
    assert ds["decision_status"] == "INSUFFICIENT"

    ds2 = {
        "factors": [{"value": "dry oily skin", "source": "customer_input", "validity": "DECLARED"}],
        "decision_status": "READY",
    }
    needs2 = svc._generate_needs_from_decision_state(ds2)
    assert needs2 == []
    assert ds2["decision_status"] == "INSUFFICIENT"
    assert ds2["ambiguous_need_factors"][0]["status"] == "uncertain"


def test_need_match_uses_explicit_controlled_product_surface():
    """Product compatibility accepts only explicitly approved product-side phrases."""
    svc = RecommendationService.__new__(RecommendationService)
    assert svc._calculate_need_match(["hydration"], "hydration") == 1.0
    assert svc._calculate_need_match(["hydration"], "آبرسانی") == 1.0
    assert svc._calculate_need_match(["hydration"], "hydration moisturizing face") == 0.0
    assert svc._calculate_need_match(["hydration"], "moisturizing face") == 0.0
    assert svc._calculate_need_match(["hydration"], "unrelated product text") == 0.0


def test_canonical_ids_are_stable_keys():
    assert "hydration" in CANONICAL_NEEDS
    assert CANONICAL_NEEDS["sun_protection"] == "sun protection"
