from types import SimpleNamespace

from app.domain.product_knowledge_gaps import (
    build_product_knowledge_gap_report,
    consultation_gap_warnings,
)


def _pk(**overrides):
    values = {
        "product_id": "synthetic-product",
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
        claim_id="claim-1", product_id="synthetic-product", conflict_status="NONE"
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
    warnings = consultation_gap_warnings(report)
    assert len(warnings) == 5
    assert all("تکمیل بعدی ثبت شده" in item for item in warnings)


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
        claim_id="claim-1", product_id="another-product", conflict_status="NONE"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "PARTIAL"


def test_unresolved_conflict_is_not_hidden_in_evidence_refs():
    evidence = [SimpleNamespace(
        claim_id="claim-1", product_id="synthetic-product", conflict_status="CONFLICT"
    )]
    report = build_product_knowledge_gap_report(_pk(), evidence)
    item = next(entry for entry in report if entry["field"] == "evidence_refs")
    assert item["status"] == "CONFLICT"
