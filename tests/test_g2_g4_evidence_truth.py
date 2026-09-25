import pytest
from app.core.auth import create_access_token
from app.models.product import Product
from app.models.customer import Customer
from app.models.case import Case
from app.models.inventory import Inventory
from app.models.user_role import UserRole, ROLE_REVIEWER_QA
from app.models.evidence import Evidence
from app.models.evidence_mutation_log import EvidenceMutationLog
from app.services.research_draft_service import ResearchDraftService
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService
from app.services.recommendation_service import RecommendationService


def _auth(db_session, subject="evidence_operator"):
    db_session.add(
        UserRole(
            user_role_id=f"UR-{subject}",
            subject_id=subject,
            role=ROLE_REVIEWER_QA,
        )
    )
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}


def _product(db_session, product_id="G2-G4-001"):
    product = Product(
        product_id=product_id,
        brand="TestBrand",
        product_name="Evidence Truth Test",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db_session.add(product)
    db_session.commit()

    db_session.add(
        Inventory(
            inventory_id=f"INV-{product_id}",
            product_id=product_id,
            quantity_available=10,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
        )
    )
    db_session.commit()
    return product


def test_research_draft_is_source_traceable_and_stays_pending(db_session):
    _product(db_session)
    rows = ResearchDraftService(db_session).create_draft(
        "G2-G4-001",
        [{
            "claim": "Supports hydration",
            "source_type": "MANUFACTURER",
            "source_reference": "label:hydration",
            "claim_type": "MANUFACTURER_CLAIM",
            "field": "known_use_cases",
        }],
        actor_id="researcher-1",
        actor_role=ROLE_REVIEWER_QA,
    )

    assert len(rows) == 1
    evidence = rows[0]
    assert evidence.product_id == "G2-G4-001"
    assert evidence.qa_status == "PENDING"
    assert evidence.evidence_status == "UNKNOWN"
    assert evidence.source_reference == "label:hydration"

    knowledge = ProductKnowledgeService(db_session).get_or_create("G2-G4-001")
    assert knowledge.known_use_cases is None


def test_research_draft_rejects_missing_source(db_session):
    _product(db_session)
    with pytest.raises(Exception):
        ResearchDraftService(db_session).create_draft(
            "G2-G4-001",
            [{
                "claim": "Supports hydration",
                "source_type": "MANUFACTURER",
                "source_reference": "",
                "claim_type": "MANUFACTURER_CLAIM",
            }],
            actor_id="researcher-1",
            actor_role=ROLE_REVIEWER_QA,
        )


def test_evidence_mutations_create_actor_bound_audit_rows(db_session):
    _product(db_session)
    service = EvidenceService(db_session)
    evidence = service.add_evidence(
        {
            "product_id": "G2-G4-001",
            "source_type": "MANUFACTURER",
            "source_reference": "ref-1",
            "claim": "Supports hydration",
            "claim_type": "MANUFACTURER_CLAIM",
            "field": "known_use_cases",
        },
        actor_id="qa-1",
        actor_role=ROLE_REVIEWER_QA,
    )
    service.verify_evidence(
        evidence.evidence_id,
        "VERIFIED",
        actor_id="qa-1",
        actor_role=ROLE_REVIEWER_QA,
        reason="Reviewed source",
    )
    logs = (
        db_session.query(EvidenceMutationLog)
        .filter(EvidenceMutationLog.target_id == evidence.evidence_id)
        .order_by(EvidenceMutationLog.timestamp.asc())
        .all()
    )

    assert [log.action for log in logs] == ["CREATE", "VERIFY"]
    assert all(log.actor_id == "qa-1" for log in logs)
    assert all(log.actor_role == ROLE_REVIEWER_QA for log in logs)
    assert logs[1].before_state is not None
    assert logs[1].after_state is not None
    assert logs[1].reason == "Reviewed source"


def test_conflict_resolution_closes_pair_and_propagates_to_knowledge_and_recommendation(db_session):
    product_id = "G2-G4-CONFLICT"
    _product(db_session, product_id)
    db_session.add(Customer(customer_id="C-G2-G4", name="Conflict Test"))
    db_session.add(Case(case_id="CASE-G2-G4", customer_id="C-G2-G4", case_type="SKIN"))
    db_session.commit()

    service = EvidenceService(db_session)
    winner = service.add_evidence(
        {
            "product_id": product_id,
            "source_type": "MANUFACTURER",
            "source_reference": "source:winner",
            "claim": "hydration",
            "claim_type": "MANUFACTURER_CLAIM",
            "field": "known_use_cases",
            "evidence_strength": "STRONG",
        },
        actor_id="qa-1",
        actor_role=ROLE_REVIEWER_QA,
    )
    loser = service.add_evidence(
        {
            "product_id": product_id,
            "source_type": "MANUFACTURER",
            "source_reference": "source:loser",
            "claim": "dry_skin_only",
            "claim_type": "MANUFACTURER_CLAIM",
            "field": "known_use_cases",
            "evidence_strength": "WEAK",
        },
        actor_id="qa-1",
        actor_role=ROLE_REVIEWER_QA,
    )

    assert winner.conflict_status == "CONFLICT"
    assert loser.conflict_status == "CONFLICT"

    service.verify_evidence(winner.evidence_id, "VERIFIED", actor_id="qa-1", actor_role=ROLE_REVIEWER_QA, reason="Winner reviewed")
    service.verify_evidence(loser.evidence_id, "VERIFIED", actor_id="qa-1", actor_role=ROLE_REVIEWER_QA, reason="Loser reviewed")

    blocked_knowledge = ProductKnowledgeService(db_session).get_or_create(product_id)
    assert blocked_knowledge.known_use_cases is None

    before = RecommendationService(db_session).generate_recommendations(
        "CASE-G2-G4",
        {"customer_id": "C-G2-G4", "concerns": "hydration"},
    )
    assert before == []

    resolved = service.resolve_conflict(
        winner.evidence_id,
        "Selected after source review",
        actor_id="qa-1",
        actor_role=ROLE_REVIEWER_QA,
    )
    assert resolved.conflict_status == "NONE"

    db_session.refresh(loser)
    assert loser.conflict_status == "NONE"
    assert loser.qa_status == "REJECTED"

    knowledge = ProductKnowledgeService(db_session).get_or_create(product_id)
    assert knowledge.known_use_cases == "hydration"
    assert knowledge.evidence_refs == winner.claim_id

    after = RecommendationService(db_session).generate_recommendations(
        "CASE-G2-G4",
        {"customer_id": "C-G2-G4", "concerns": "hydration"},
    )
    assert len(after) == 1
    assert after[0].product_id == product_id
    assert after[0].eligibility_status == "ELIGIBLE"
    assert after[0].evidence_refs


def test_evidence_api_requires_role_for_mutation_and_exposes_audit(client, db_session):
    _product(db_session)
    headers = _auth(db_session)
    payload = {
        "product_id": "G2-G4-001",
        "claim": "Supports hydration",
        "source_type": "MANUFACTURER",
        "source_reference": "ref-api",
        "claim_type": "MANUFACTURER_CLAIM",
        "field": "known_use_cases",
    }
    response = client.post("/api/v1/evidence/", json=payload, headers=headers)
    assert response.status_code == 201
    evidence_id = response.json()["evidence_id"]

    audit = client.get(f"/api/v1/evidence/{evidence_id}/audit", headers=headers)
    assert audit.status_code == 200
    assert len(audit.json()) == 1
    assert audit.json()[0]["actor_id"] == "evidence_operator"
