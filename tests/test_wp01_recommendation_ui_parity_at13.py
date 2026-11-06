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
    assert "const list = await generateRecommendations(" in source
    assert "const publicList = Array.isArray(list) ? list : [];" in source
    assert "setRecs(publicList);" in source
    assert "setRecDone(true);" in source
    assert 'setActive("results");' in source

    # Customer-visible results must be committed to UI state before the
    # optional operator session is requested. A missing operator token must
    # never turn a completed customer consultation into a failed flow.
    publish_at = source.index("// Publish customer-visible results immediately; operator access is optional.")
    operator_at = source.index("const operatorToken = await ensureProductSession();", publish_at)
    assert publish_at < operator_at
    assert "listInternalEvaluationsByCase(newCaseId, operatorToken)" in source


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
