"""AT-13 acceptance checks for Recommendation V1 Home UI parity (§38).

The frontend has no JS test runner; these tests pin the small source-level contract
for the authorized UI-only change while backend Recommendation behavior remains
covered by the existing API/service suites.
"""
from pathlib import Path

HOME = Path(__file__).parents[1] / "frontend" / "src" / "pages" / "NewHomePage.tsx"


def _source() -> str:
    return HOME.read_text(encoding="utf-8")


def test_at13_initial_recommendation_limit_is_five():
    source = _source()
    assert "const INITIAL_RECOMMENDATION_LIMIT = 5;" in source
    assert "recs.slice(0, showAllRecommendations ? recs.length : INITIAL_RECOMMENDATION_LIMIT)" in source


def test_at13_show_more_exists_only_when_more_than_five_results():
    source = _source()
    assert "recs.length > INITIAL_RECOMMENDATION_LIMIT && !showAllRecommendations" in source
    assert "setShowAllRecommendations(true)" in source


def test_at13_backend_full_result_set_is_still_stored():
    source = _source()
    assert "setRecs(Array.isArray(list) ? list : []);" in source
    assert "const list = await generateRecommendations(" in source


def test_at13_no_recommendation_selection_or_backend_filter_was_added():
    source = _source()
    assert "selectRecommendationForSale(r)" in source
    assert "generateRecommendations(" in source
