"""
Unit tests for ReasoningEngine (GATE 7-3 + scoring integration)
TEST EVIDENCE — NOT YET QA APPROVED
"""
import pytest
from app.reasoning.reasoning_engine import ReasoningEngine


@pytest.fixture
def engine():
    return ReasoningEngine()


def test_run_returns_computed_only(engine):
    result = engine.run(product_id="P001")
    assert result["persistence"] == "COMPUTED_ONLY"
    assert "engine_version" in result
    assert "generated_at" in result


def test_run_empty_inputs(engine):
    result = engine.run(product_id="P001")
    assert result["product_id"] == "P001"
    assert result["evidence_refs"] == []
    assert result["conflicts"] == []
    assert result["unknowns"] == []
    assert result["claim_boundary_violations"] == []
    assert "Evidence items considered: 0" in result["rationale"]


def test_run_builds_evidence_refs(engine):
    evidence = [
        {
            "evidence_id": "EV1",
            "claim_id": "C1",
            "field": "ingredients",
            "claim_type": "FACT",
            "source_reference": "DOI:123",
            "source_type": "PEER_REVIEWED",
            "evidence_strength": "STRONG",
            "qa_status": "VERIFIED",
        }
    ]
    result = engine.run(product_id="P001", evidence_list=evidence)
    assert len(result["evidence_refs"]) == 1
    ref = result["evidence_refs"][0]
    assert ref["evidence_id"] == "EV1"
    assert ref["source"] == "DOI:123"
    assert ref["evidence_strength"] == "STRONG"


def test_run_surfaces_unknowns(engine):
    evidence = [
        {
            "evidence_id": "EV_UNK",
            "claim_type": "UNKNOWN",
            "field": "brand",
            "claim": "identity unclear",
        }
    ]
    result = engine.run(product_id="P001", evidence_list=evidence)
    assert len(result["unknowns"]) == 1
    unk = result["unknowns"][0]
    assert unk["product_id"] == "P001"
    assert unk["field"] == "brand"
    assert unk["severity"] == "CRITICAL"
    assert unk["action"] == "ESCALATE_PO"


def test_run_detects_claim_boundary_violations(engine):
    evidence = [
        {
            "claim_type": "MANUFACTURER_CLAIM",
            "target_type": "FACT",
            "claim": "Cures acne",
        },
        {
            "claim_type": "FACT",
            "target_type": "FACT",
            "claim": "Contains SPF 50",
        },
    ]
    result = engine.run(product_id="P001", evidence_list=evidence)
    assert len(result["claim_boundary_violations"]) == 1
    assert result["claim_boundary_violations"][0]["from_type"] == "MANUFACTURER_CLAIM"
    assert result["claim_boundary_violations"][0]["allowed"] is False


def test_run_analyzes_existing_conflicts(engine):
    existing = [
        {
            "field": "brand",
            "values": ["ISDIN", "Isdin"],
            "sources": ["src1", "src2"],
        }
    ]
    result = engine.run(product_id="P001", existing_conflicts=existing)
    assert len(result["conflicts"]) == 1
    conf = result["conflicts"][0]
    assert conf["severity"] == "CRITICAL"
    assert conf["auto_resolution_allowed"] is False
    assert conf["resolution_state"] == "UNRESOLVED"
    assert "HIGH/CRITICAL" in result["rationale"]


def test_run_never_mutates_input(engine):
    evidence = [{"claim_type": "FACT", "claim": "test"}]
    original = list(evidence)
    engine.run(product_id="P001", evidence_list=evidence)
    assert evidence == original


def test_run_with_product_knowledge_snapshot(engine):
    pk = {"ingredients": "salicylic acid", "claimed_benefits": "oil control"}
    result = engine.run(product_id="P001", product_knowledge_snapshot=pk)
    assert result["product_knowledge_snapshot"] == pk


def test_run_with_scoring_inputs_returns_final_score(engine):
    result = engine.run(
        product_id="P001",
        need_match=0.8,
        evidence_score=0.6,
        inventory_score=1.0,
    )
    assert "final_score" in result
    assert "evidence_score" in result
    assert result["evidence_score"] == 0.6
    assert result["eligibility"] in (
        "ELIGIBLE",
        "NEEDS_REVIEW",
        "INELIGIBLE",
    )
    assert result["persistence"] == "COMPUTED_ONLY"
