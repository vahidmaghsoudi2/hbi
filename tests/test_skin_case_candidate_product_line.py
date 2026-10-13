from types import SimpleNamespace

from app.services.recommendation_service import _candidate_matches_case_product_line


def test_skin_case_excludes_non_skin_candidates():
    assert _candidate_matches_case_product_line(
        SimpleNamespace(product_line="SKIN"), "SKIN"
    )
    assert not _candidate_matches_case_product_line(
        SimpleNamespace(product_line="HAIR"), "SKIN"
    )
    assert not _candidate_matches_case_product_line(
        SimpleNamespace(product_line=None), "SKIN"
    )


def test_non_skin_or_legacy_case_type_keeps_existing_candidate_behavior():
    assert _candidate_matches_case_product_line(
        SimpleNamespace(product_line="HAIR"), "OPEN"
    )
    assert _candidate_matches_case_product_line(
        SimpleNamespace(product_line=None), None
    )
