import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_problem_link import ProductProblemLink
from app.services.product_problem_link_service import ProductProblemLinkService


def _product(db, product_id="PPL-PRODUCT-001", market_region=None):
    product = Product(
        product_id=product_id,
        brand="ISDIN",
        product_name="FotoUltra 100 Active Unify SPF50+",
        identity_status="PARTIAL_IDENTITY",
        qa_verdict="PENDING",
        status="DRAFT",
        market_region=market_region,
    )
    db.add(product)
    db.flush()
    return product


def _evidence(db, product_id, evidence_id="EV-PPL-001", claim_id="EV-PPL-CLAIM-001",
              market_region="MEXICO", qa_status="PENDING", conflict_status="NONE"):
    evidence = Evidence(
        evidence_id=evidence_id,
        product_id=product_id,
        claim_id=claim_id,
        source_type="MANUFACTURER",
        source_reference="manufacturer-data-on-file",
        claim="Manufacturer-reported reduction in visible dark-spot intensity.",
        field="claim",
        market_region=market_region,
        claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN",
        evidence_strength="UNVERIFIED",
        qa_status=qa_status,
        conflict_status=conflict_status,
    )
    db.add(evidence)
    db.flush()
    return evidence


def _candidate_payload(product, evidence, **overrides):
    payload = {
        "product_id": product.product_id,
        "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id,
        "problem_id": "P17",
        "problem_type": "Problem/presentation",
        "problem_definition_ref": "SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        "relationship_role": "presentation",
        "relationship_status": "CANDIDATE",
        "semantic_basis": (
            "The manufacturer claim concerns visible dark spots and is therefore "
            "a limited presentation-level semantic candidate for P17 only."
        ),
        "limitations": (
            "Manufacturer-reported data on file; HBI SKU identity and variant are "
            "not verified; no cause-specific inference is permitted."
        ),
        "decision_basis": (
            "Identity is PARTIAL_IDENTITY and Evidence QA is PENDING; "
            "SUPPORTED and Recommendation are prohibited."
        ),
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": "UNKNOWN",
        "market_region": "MEXICO",
    }
    payload.update(overrides)
    return payload


def test_create_candidate_is_evidence_anchored_and_does_not_change_product_knowledge(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)

    link = service.create_link(**_candidate_payload(product, evidence))

    assert link.relationship_status == "CANDIDATE"
    assert link.problem_id == "P17"
    assert link.evidence_id == evidence.evidence_id
    assert link.claim_id == evidence.claim_id
    assert link.product_id == product.product_id
    assert db_session.query(ProductProblemLink).count() == 1
    assert db_session.query(ProductKnowledge).filter(
        ProductKnowledge.product_id == product.product_id
    ).first() is None


def test_supported_status_is_not_persistable_in_this_phase(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="SUPPORTED is disabled"):
        service.create_link(**_candidate_payload(
            product, evidence, relationship_status="SUPPORTED"
        ))

    assert db_session.query(ProductProblemLink).count() == 0


def test_evidence_must_belong_to_the_same_product(db_session):
    product = _product(db_session)
    other = _product(db_session, product_id="PPL-PRODUCT-002")
    evidence = _evidence(db_session, other.product_id)
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="same product"):
        service.create_link(**_candidate_payload(product, evidence))

    assert db_session.query(ProductProblemLink).count() == 0


def test_p22_cannot_receive_an_independent_product_problem_link(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        service.create_link(**_candidate_payload(product, evidence, problem_id="P22"))

    assert db_session.query(ProductProblemLink).count() == 0


def test_unknown_problem_code_is_rejected(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="P01-P61"):
        service.create_link(**_candidate_payload(product, evidence, problem_id="P99"))


def test_product_and_evidence_market_must_match_link_market(db_session):
    product = _product(db_session, market_region="EUROPE")
    evidence = _evidence(db_session, product.product_id, market_region="MEXICO")
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="Product market"):
        service.create_link(**_candidate_payload(
            product, evidence, market_region="MEXICO"
        ))


def test_conflicted_or_rejected_evidence_cannot_anchor_a_link(db_session):
    product = _product(db_session)
    conflicted = _evidence(
        db_session, product.product_id, evidence_id="EV-PPL-CONFLICT",
        claim_id="EV-PPL-CONFLICT-CLAIM", conflict_status="CONFLICT"
    )
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="Conflicted Evidence"):
        service.create_link(**_candidate_payload(product, conflicted))

    rejected = _evidence(
        db_session, product.product_id, evidence_id="EV-PPL-REJECTED",
        claim_id="EV-PPL-REJECTED-CLAIM", qa_status="REJECTED"
    )
    with pytest.raises(ValidationError, match="Rejected Evidence"):
        service.create_link(**_candidate_payload(product, rejected))

    assert db_session.query(ProductProblemLink).count() == 0


def test_market_and_semantic_fields_are_required(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)

    with pytest.raises(ValidationError, match="semantic_basis is required"):
        service.create_link(**_candidate_payload(product, evidence, semantic_basis=" "))

    with pytest.raises(ValidationError, match="market_region is required"):
        service.create_link(**_candidate_payload(product, evidence, market_region=""))


def test_duplicate_link_scope_is_rejected_by_database_constraint(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    payload = _candidate_payload(product, evidence)

    service.create_link(**payload)
    with pytest.raises(Exception):
        service.create_link(**payload)

    assert db_session.query(ProductProblemLink).count() == 0
