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
    assert "eligibleRecs.slice(0, showAllRecommendations ? eligibleRecs.length : INITIAL_RECOMMENDATION_LIMIT)" in source


def test_at13_show_more_exists_only_when_more_than_five_results():
    source = _source()
    assert "eligibleRecs.length > INITIAL_RECOMMENDATION_LIMIT && !showAllRecommendations" in source
    assert "setShowAllRecommendations(true)" in source


def test_at13_customer_results_are_published_before_optional_operator_enrichment():
    source = _source()
    assert "listRecommendationsByCase" in source

    generate_start = source.index("const list = await generateRecommendations(")
    generated_public_list = source.index("const publicList = Array.isArray(list) ? list : [];", generate_start)
    generated_publish = source.index("setRecs(publicList);", generated_public_list)
    generated_done = source.index("setRecDone(true);", generated_publish)
    generated_results = source.index('setActive("results");', generated_done)
    generated_operator = source.index("const operatorToken = await ensureProductSession();", generated_results)
    assert generated_public_list < generated_publish < generated_done < generated_results < generated_operator

    refresh_start = source.index("const publicList = await listRecommendationsByCase(storedCaseId, token);")
    refresh_publish = source.index("setRecs(Array.isArray(publicList) ? publicList : []);", refresh_start)
    refresh_done = source.index("setRecDone(true);", refresh_publish)
    refresh_operator = source.index("const operatorToken = await ensureProductSession();", refresh_done)
    assert refresh_start < refresh_publish < refresh_done < refresh_operator


def test_at13_consultation_recommendations_remain_separate_from_direct_sale():
    source = _source()
    assert "generateRecommendations(" in source
    assert "selectRecommendationForSale(r)" not in source
    assert "selectedRecommendationId" not in source

    # Direct sale accepts an explicitly chosen customer, but is not coupled to
    # a consultation recommendation. Consultation/accounting linkage belongs
    # to the consultation flow, not as a prerequisite in the sales form.
    sale_call = source.split("const sale = await createSale(", 1)[1].split("setLastSale", 1)[0]
    assert "recommendation_id" not in sale_call
