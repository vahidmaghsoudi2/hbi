import pytest

from app.core.auth import create_access_token
from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.user_role import UserRole, ROLE_REVIEWER_QA
from app.services.product_problem_link_service import ProductProblemLinkService
from app.services.product_problem_candidate_retrieval_service import (
    ProductProblemCandidateRetrievalService,
)


def _seed(db, suffix="1", *, market="MEXICO", variant="UNKNOWN"):
    product = Product(
        product_id=f"RETRIEVAL-PRODUCT-{suffix}",
        brand="Test Brand",
        product_name=f"Test Product {suffix}",
        identity_status="PARTIAL_IDENTITY",
        qa_verdict="PENDING",
        status="DRAFT",
        market_region=market,
    )
    db.add(product)
    db.flush()
    evidence = Evidence(
        evidence_id=f"RETRIEVAL-EVIDENCE-{suffix}",
        product_id=product.product_id,
        claim_id=f"RETRIEVAL-CLAIM-{suffix}",
        source_type="MANUFACTURER",
        source_reference=f"test-source-{suffix}",
        claim="Manufacturer-reported visible dark-spot appearance claim.",
        field="claim",
        market_region=market,
        claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN",
        evidence_strength="UNVERIFIED",
        qa_status="PENDING",
        conflict_status="NONE",
    )
    db.add(evidence)
    db.flush()
    payload = {
        "product_id": product.product_id,
        "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id,
        "problem_id": "P17",
        "problem_type": "Problem/presentation",
        "problem_definition_ref": "SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        "relationship_role": "presentation",
        "relationship_status": "CANDIDATE",
        "feature_basis": "The exact selected manufacturer claim about visible dark spots.",
        "outcome": "Visible appearance endpoint only; no cause or diagnosis.",
        "semantic_basis": "A limited presentation-level candidate for P17 only.",
        "limitations": "Manufacturer claim; product identity and Evidence QA are not verified.",
        "decision_basis": "Human review only; no suitability or recommendation decision.",
        "reason": "Candidate retrieval test.",
        "idempotency_key": f"retrieval-key-{suffix}-0001",
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": variant,
        "market_region": market,
    }
    link = ProductProblemLinkService(db).create_link(**payload)
    return product, evidence, link, payload


def test_retrieval_returns_only_current_candidate_and_exposes_all_blockers(db_session):
    product, evidence, link, _ = _seed(db_session)
    result = ProductProblemCandidateRetrievalService(db_session).retrieve("p17")

    assert result["problem_id"] == "P17"
    assert result["retrieval_mode"] == "CURRENT_CANDIDATES_ONLY"
    assert result["review_gate"] == "HUMAN_REVIEW_ONLY"
    assert result["recommendation_eligible"] is False
    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["link_id"] == link.link_id
    assert candidate["product_id"] == product.product_id
    assert candidate["evidence_id"] == evidence.evidence_id
    assert candidate["relationship_status"] == "CANDIDATE"
    assert candidate["product_gate_status"] == "BLOCKED"
    assert set(candidate["product_gate_blockers"]) == {
        "PRODUCT_IDENTITY_NOT_VERIFIED",
        "PRODUCT_QA_NOT_VALID",
        "PRODUCT_NOT_ACTIVE",
        "EVIDENCE_NOT_VERIFIED",
        "VARIANT_UNKNOWN",
    }


def test_retrieval_is_market_neutral_but_keeps_variant_filter(db_session):
    _seed(db_session, "mx", market="MEXICO", variant="COLOR")
    _seed(db_session, "uk", market="UK", variant="NON_COLOR")
    service = ProductProblemCandidateRetrievalService(db_session)

    mexico = service.retrieve("P17", market_region="mexico", variant="COLOR")
    uk = service.retrieve("P17", market_region="UK", variant="NON_COLOR")
    canada = service.retrieve("P17", market_region="CANADA")

    assert [row["market_region"] for row in mexico["candidates"]] == ["MEXICO"]
    assert [row["market_region"] for row in uk["candidates"]] == ["UK"]
    assert canada["candidate_count"] == 2
    assert {row["market_region"] for row in canada["candidates"]} == {"MEXICO", "UK"}
    assert canada["market_scope_mode"] == "MARKET_NEUTRAL"
    assert canada["market_filter_applied"] is False
    assert canada["requested_market_region"] == "CANADA"


def test_retrieval_preserves_product_evidence_and_link_market_provenance(db_session):
    product, evidence, link, _ = _seed(db_session, "provenance", market="MEXICO")
    product.market_region = "EU"
    evidence.market_region = "US"
    link.market_region = "MEXICO"
    db_session.flush()

    result = ProductProblemCandidateRetrievalService(db_session).retrieve(
        "P17", market_region="CANADA"
    )

    candidate = result["candidates"][0]
    assert result["market_filter_applied"] is False
    assert candidate["product_market_region"] == "EU"
    assert candidate["evidence_market_region"] == "US"
    assert candidate["market_region"] == "MEXICO"


def test_retrieval_uses_latest_revision_and_hides_superseded_candidate(db_session):
    product, evidence, first, payload = _seed(db_session, "revision")
    revised_payload = dict(payload)
    revised_payload.update({
        "relationship_status": "DEFERRED",
        "reason": "Deferred pending product identity verification.",
        "idempotency_key": "retrieval-key-revision-0002",
    })
    ProductProblemLinkService(db_session).reassess_link(
        first.link_id,
        expected_revision_no=1,
        actor_id="reviewer-1",
        actor_role="REVIEWER_QA",
        **revised_payload,
    )

    result = ProductProblemCandidateRetrievalService(db_session).retrieve("P17")
    assert result["candidate_count"] == 0


def test_retrieval_rejects_p22_context_only_and_invalid_problem_ids(db_session):
    service = ProductProblemCandidateRetrievalService(db_session)
    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        service.retrieve("P22")
    with pytest.raises(ValidationError, match="P01-P61"):
        service.retrieve("P99")


def test_candidate_retrieval_api_is_role_protected_and_read_only(client, db_session):
    _product, _evidence, _link, _payload = _seed(db_session, "api")
    db_session.commit()
    subject = "candidate-retrieval-reviewer"
    db_session.add(UserRole(
        user_role_id=f"TEST-{subject}-REVIEWER_QA",
        subject_id=subject,
        role=ROLE_REVIEWER_QA,
    ))
    db_session.commit()
    headers = {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}

    unauthorized = client.get(
        "/api/v1/product-problem-links/candidates",
        params={"problem_id": "P17"},
    )
    response = client.get(
        "/api/v1/product-problem-links/candidates",
        params={"problem_id": "P17"},
        headers=headers,
    )

    assert unauthorized.status_code == 401
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["candidate_count"] == 1
    assert body["recommendation_eligible"] is False
    assert body["candidates"][0]["review_gate"] == "HUMAN_REVIEW_ONLY"
