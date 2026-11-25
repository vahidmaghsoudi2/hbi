import json

import pytest

from app.core.exceptions import ValidationError
from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.case_service import CaseService
from app.services.explainable_suitability_service import ExplainableSuitabilityService
from app.services.product_problem_link_service import ProductProblemLinkService


def _seed_candidate(db, *, suffix="1", product_state="DRAFT", qa="PENDING",
                    identity="PARTIAL_IDENTITY", evidence_qa="PENDING",
                    variant="UNKNOWN"):
    product = Product(
        product_id=f"XS-PRODUCT-{suffix}",
        brand="Test Brand",
        product_name=f"Test Product {suffix}",
        identity_status=identity,
        qa_verdict=qa,
        status=product_state,
        market_region="MEXICO",
    )
    db.add(product)
    db.flush()
    evidence = Evidence(
        evidence_id=f"XS-EVIDENCE-{suffix}",
        product_id=product.product_id,
        claim_id=f"XS-CLAIM-{suffix}",
        source_type="MANUFACTURER",
        source_reference=f"test-source-{suffix}",
        claim="Manufacturer-reported visible dark-spot appearance claim.",
        field="claim",
        market_region="MEXICO",
        claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN",
        evidence_strength="UNVERIFIED",
        qa_status=evidence_qa,
        conflict_status="NONE",
    )
    db.add(evidence)
    db.flush()
    link = ProductProblemLinkService(db).create_link(
        product_id=product.product_id,
        evidence_id=evidence.evidence_id,
        claim_id=evidence.claim_id,
        problem_id="P17",
        problem_type="Problem/presentation",
        problem_definition_ref="SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        relationship_role="presentation",
        relationship_status="CANDIDATE",
        feature_basis="Exact selected manufacturer claim about visible dark spots.",
        outcome="Visible appearance endpoint only; no cause or diagnosis.",
        semantic_basis="Limited presentation-level candidate for P17 only.",
        limitations="Manufacturer claim; no clinical efficacy inference.",
        decision_basis="Human review only; no suitability or recommendation decision.",
        reason="Stage 13-14 explainability test.",
        idempotency_key=f"xs-retrieval-{suffix}-0001",
        problem_map_version="SKIN_PROBLEM_SPACE_MAP_V0.1",
        variant=variant,
        market_region="MEXICO",
        actor_id="test-reviewer",
        actor_role="REVIEWER_QA",
    )
    return product, evidence, link


def test_explainable_suitability_exposes_blockers_without_approving_candidate(db_session):
    product, evidence, link = _seed_candidate(db_session)
    result = ExplainableSuitabilityService(db_session).evaluate(
        "P17", market_region="MEXICO", variant="UNKNOWN"
    )

    assert result["evaluation_mode"] == "EXPLAINABLE_HUMAN_REVIEW_ONLY"
    assert result["computed_only"] is True
    assert result["recommendation_eligible"] is False
    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["link_id"] == link.link_id
    assert candidate["product_id"] == product.product_id
    assert candidate["evidence_id"] == evidence.evidence_id
    assert candidate["suitability_status"] == "BLOCKED"
    assert "PRODUCT_IDENTITY_NOT_VERIFIED" in candidate["product_gate_blockers"]
    assert candidate["recommendation_eligible"] is False


def test_candidate_with_clear_gates_still_requires_human_review(db_session):
    _seed_candidate(
        db_session,
        suffix="reviewable",
        product_state="ACTIVE",
        qa="VALID",
        identity="VERIFIED",
        evidence_qa="VERIFIED",
        variant="NON_COLOR",
    )
    result = ExplainableSuitabilityService(db_session).evaluate(
        "P17", market_region="MEXICO", variant="NON_COLOR"
    )

    candidate = result["candidates"][0]
    assert candidate["suitability_status"] == "HUMAN_REVIEW_REQUIRED"
    assert candidate["product_gate_blockers"] == []
    assert candidate["relationship_status"] == "CANDIDATE"
    assert candidate["recommendation_eligible"] is False


def test_explainable_suitability_rejects_context_only_p22(db_session):
    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        ExplainableSuitabilityService(db_session).evaluate("P22")


def test_consultation_output_preserves_visit_context_and_hides_rejected_rows(db_session):
    customer = Customer(
        customer_id="XS-CUSTOMER",
        name="Test Customer",
        consent_to_store_data=1,
    )
    db_session.add(customer)
    case = Case(case_id="XS-CASE", customer_id=customer.customer_id, case_type="SKIN")
    db_session.add(case)

    eligible = Product(
        product_id="XS-ELIGIBLE",
        brand="Test Brand",
        product_name="Eligible Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    rejected = Product(
        product_id="XS-REJECTED",
        brand="Test Brand",
        product_name="Rejected Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db_session.add_all([eligible, rejected])
    db_session.flush()
    db_session.add_all([
        Recommendation(
            recommendation_id="XS-REC-ELIGIBLE",
            case_id=case.case_id,
            product_id=eligible.product_id,
            eligibility_status="ELIGIBLE",
            need_match_score=0.8,
            evidence_score=0.9,
            ranking_score=0.85,
            warnings=json.dumps(["اطلاعات مصرف ناقص است."], ensure_ascii=False),
        ),
        Recommendation(
            recommendation_id="XS-REC-REJECTED",
            case_id=case.case_id,
            product_id=rejected.product_id,
            eligibility_status="INELIGIBLE_PENDING_REVIEW",
            exclusion_reasons='["NO_APPROVED_EVIDENCE"]',
        ),
    ])
    db_session.flush()
    context = {
        "affected_areas": ["cheek"],
        "duration": "two weeks",
        "severity": 5,
        "aggravating_factors": ["sun exposure"],
        "current_products": ["cleanser"],
        "notes": None,
    }
    CaseService(db_session).save_consultation_context(case.case_id, context)

    result = ExplainableSuitabilityService(db_session).consultation_output(case.case_id)

    assert result["consultation_context"] == context
    assert result["consultation_context_status"] == "PRESENT"
    assert result["recommendation_status"] == "RECOMMENDATIONS_AVAILABLE"
    assert [row["product_id"] for row in result["recommendations"]] == [eligible.product_id]
    assert result["recommendations"][0]["eligibility_status"] == "ELIGIBLE"
    assert "exclusion_reasons" not in result["recommendations"][0]
    assert result["computed_only"] is True


def test_consultation_output_reports_no_approved_recommendation(db_session):
    customer = Customer(
        customer_id="XS-CUSTOMER-EMPTY",
        name="Test Customer",
        consent_to_store_data=1,
    )
    db_session.add(customer)
    db_session.add(Case(
        case_id="XS-CASE-EMPTY",
        customer_id=customer.customer_id,
        case_type="SKIN",
    ))
    db_session.flush()

    result = ExplainableSuitabilityService(db_session).consultation_output("XS-CASE-EMPTY")

    assert result["consultation_context_status"] == "NOT_RECORDED"
    assert result["recommendation_status"] == "NO_APPROVED_RECOMMENDATION"
    assert result["recommendation_count"] == 0
    assert result["recommendations"] == []
