"""GAP-05 L1 — Controlled Semantic Need Normalization tests (contract acceptance)."""
from app.services.need_normalization import (
    map_phrase_to_canonical,
    normalize_needs_from_factors,
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


def test_unmapped_remains_explicit():
    factors = [
        {"name": "concern", "value": "آبرسان", "source": "customer_input", "validity": "DECLARED"},
        {"name": "concern", "value": "something_unmapped_zzz", "source": "customer_input", "validity": "DECLARED"},
    ]
    needs, mappings, unmapped = normalize_needs_from_factors(factors)
    assert needs == ["hydration"]
    assert len(mappings) == 1
    assert mappings[0]["canonical"] == "hydration"
    assert mappings[0]["rule"] == "approved_synonym_map"
    assert len(unmapped) == 1
    assert unmapped[0]["factor_value"] == "something_unmapped_zzz"
    assert unmapped[0]["reason"] == "no_approved_mapping"


def test_determinism():
    factors = [
        {"value": "sunscreen"},
        {"value": "ضدآفتاب"},
        {"value": "spf"},
    ]
    n1, m1, u1 = normalize_needs_from_factors(factors)
    n2, m2, u2 = normalize_needs_from_factors(factors)
    assert n1 == n2 == ["sun protection"]
    assert len(m1) == len(m2) == 3
    assert u1 == u2 == []


def test_traceability_factor_to_need():
    factors = [{"value": "acne", "source": "customer_input", "validity": "DECLARED"}]
    needs, mappings, unmapped = normalize_needs_from_factors(factors)
    assert needs == ["acne care"]
    assert mappings[0]["factor_value"] == "acne"
    assert mappings[0]["source"] == "customer_input"
    assert mappings[0]["validity"] == "DECLARED"
    assert unmapped == []


def test_decision_state_path_sets_audit_fields():
    svc = RecommendationService.__new__(RecommendationService)
    ds = {
        "factors": [
            {"value": "hydration", "source": "customer_input", "validity": "DECLARED"},
            {"value": "not_in_map_abc", "source": "customer_input", "validity": "DECLARED"},
        ],
        "decision_status": "READY",
    }
    needs = svc._generate_needs_from_decision_state(ds)
    assert needs == ["hydration"]
    assert ds["need_mappings"][0]["canonical"] == "hydration"
    assert ds["unmapped_need_factors"][0]["factor_value"] == "not_in_map_abc"


def test_only_unmapped_marks_insufficient():
    svc = RecommendationService.__new__(RecommendationService)
    ds = {
        "factors": [{"value": "totally_unknown_phrase_qqq", "source": "customer_input", "validity": "DECLARED"}],
        "decision_status": "READY",
    }
    needs = svc._generate_needs_from_decision_state(ds)
    assert needs == []
    assert ds["decision_status"] == "INSUFFICIENT"


def test_need_match_uses_canonical_surface_unchanged_formula():
    """Frozen formula: intersection / len(need_tokens); input may be canonical."""
    svc = RecommendationService.__new__(RecommendationService)
    score = svc._calculate_need_match(["hydration"], "hydration moisturizing face")
    assert score > 0.0
    score2 = svc._calculate_need_match(["hydration"], "unrelated product text")
    assert score2 == 0.0


def test_canonical_ids_are_stable_keys():
    assert "hydration" in CANONICAL_NEEDS
    assert CANONICAL_NEEDS["sun_protection"] == "sun protection"
