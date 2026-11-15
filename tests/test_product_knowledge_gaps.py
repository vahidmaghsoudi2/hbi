from types import SimpleNamespace

from app.domain.product_knowledge_gaps import (
    build_product_knowledge_gap_report,
    consultation_gap_warnings,
    evaluate_product_knowledge_completeness,
)


def _pk(**overrides):
    values = {
        "product_id": "synthetic-product",
        "market_region": "EU",
        "ingredients": "glycerin",
        "known_use_cases": "hydration",
        "usage_instructions": "apply daily",
        "contraindications": "avoid eye area",
        "evidence_refs": '["claim-1"]',
        "domain_evidence_status": (
            '{"ingredients":"SUPPORTED","known_use_cases":"SUPPORTED",'
            '"usage_instructions":"SUPPORTED","contraindications":"SUPPORTED"}'
        ),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_complete_synthetic_pk_has_no_ordinary_gaps():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product", market_region="EU", conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    assert [item["status"] for item in report] == [
        "SUPPORTED", "SUPPORTED", "SUPPORTED", "SUPPORTED", "SUPPORTED"
    ]
    assert consultation_gap_warnings(report) == []


def test_missing_pk_reports_all_five_fields_without_excluding_candidate():
    report = build_product_knowledge_gap_report(None, [])
    assert len(report) == 5
    assert all(item["status"] == "MISSING" for item in report)
    evaluation = evaluate_product_knowledge_completeness(None, [])
    warnings = consultation_gap_warnings(
        report, pk_record_missing=evaluation["pk_record_missing"]
    )
    assert evaluation["status"] == "partial"
    assert evaluation["missing_domains"] == [
        "ingredients", "known_use_cases", "usage_instructions",
        "contraindications", "evidence_refs",
    ]
    assert evaluation["contraindications_unreviewed"] is True
    assert any("هشدار جدی PK" in item for item in warnings)
    assert any("موارد منع مصرف" in item for item in warnings)


def test_each_knowledge_field_is_reported_when_missing():
    for field, *_ in (
        ("ingredients",), ("known_use_cases",), ("usage_instructions",),
        ("contraindications",), ("evidence_refs",),
    ):
        report = build_product_knowledge_gap_report(_pk(**{field: "  "}), [])
        item = next(entry for entry in report if entry["field"] == field)
        assert item["status"] == "MISSING"


def test_blank_contraindications_is_missing_not_clearance():
    report = build_product_knowledge_gap_report(_pk(contraindications=None), [])
    item = next(entry for entry in report if entry["field"] == "contraindications")
    assert item["status"] == "MISSING"
    assert "بدون منع مصرف" not in item["message"]


def test_text_without_domain_review_is_not_assessed():
    report = build_product_knowledge_gap_report(_pk(domain_evidence_status="{}"), [])
    item = next(entry for entry in report if entry["field"] == "ingredients")
    assert item["status"] == "NOT_ASSESSED"


def test_wrong_product_evidence_reference_is_reported_as_partial():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="another-product", market_region="EU", conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "PARTIAL"


def test_unresolved_conflict_is_not_hidden_in_evidence_refs():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product", market_region="EU", conflict_status="CONFLICT"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "CONFLICT"


def test_evidence_market_mismatch_is_reported_as_partial():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region="US", conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "PARTIAL"
    assert "بازار" in item["message"]


def test_unknown_market_scope_is_not_assumed_compatible():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region=None, conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "PARTIAL"
    assert "قابل تأیید نیست" in item["message"]


def test_evidence_reference_report_discloses_packaging_traceability_limit():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region="EU", conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert "نسخه بسته‌بندی" in item["message"]



def test_completeness_evaluator_returns_complete_status_for_supported_pk():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region="EU", conflict_status="NONE"
    )]
    result = evaluate_product_knowledge_completeness(_pk(), evidence)
    assert result["status"] == "complete"
    assert result["missing_domains"] == []
    assert result["contraindications_unreviewed"] is False
    assert result["pk_record_missing"] is False


def test_one_missing_domain_is_partial_and_does_not_mark_contraindications_unreviewed():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region="EU", conflict_status="NONE"
    )]
    result = evaluate_product_knowledge_completeness(
        _pk(ingredients=None), evidence
    )
    assert result["status"] == "partial"
    assert result["missing_domains"] == ["ingredients"]
    assert result["contraindications_unreviewed"] is False


def test_two_missing_domains_are_reported_without_candidate_policy():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product",
        market_region="EU", conflict_status="NONE"
    )]
    result = evaluate_product_knowledge_completeness(
        _pk(ingredients=None, usage_instructions=""), evidence
    )
    assert result["status"] == "partial"
    assert result["missing_domains"] == ["ingredients", "usage_instructions"]
    assert len(result["incomplete_domains"]) == 2
    assert result["contraindications_unreviewed"] is False


def test_missing_contraindications_sets_unreviewed_flag_not_safety_clearance():
    result = evaluate_product_knowledge_completeness(
        _pk(contraindications=None), []
    )
    assert result["contraindications_unreviewed"] is True
    warnings = consultation_gap_warnings(result["domain_report"])
    assert any("موارد منع مصرف هنوز بررسی/تأیید نشده‌اند" in item for item in warnings)
