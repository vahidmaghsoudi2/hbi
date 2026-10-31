import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.product_problem_link_repository import ProductProblemLinkRepository
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_problem_link import ProductProblemLink
from app.models.product_problem_link_assessment_event import ProductProblemLinkAssessmentEvent
from app.services.product_problem_link_service import ProductProblemLinkService


def _product(db, product_id="PPL-PRODUCT-001", market_region=None):
    product = Product(
        product_id=product_id, brand="ISDIN",
        product_name="FotoUltra 100 Active Unify SPF50+",
        identity_status="PARTIAL_IDENTITY", qa_verdict="PENDING",
        status="DRAFT", market_region=market_region,
    )
    db.add(product)
    db.flush()
    return product


def _evidence(db, product_id, evidence_id="EV-PPL-001", claim_id="EV-PPL-CLAIM-001",
              market_region="MEXICO", qa_status="PENDING", conflict_status="NONE"):
    evidence = Evidence(
        evidence_id=evidence_id, product_id=product_id, claim_id=claim_id,
        source_type="MANUFACTURER", source_reference="manufacturer-data-on-file",
        claim="Manufacturer-reported reduction in visible dark-spot intensity.",
        field="claim", market_region=market_region, claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN", evidence_strength="UNVERIFIED",
        qa_status=qa_status, conflict_status=conflict_status,
    )
    db.add(evidence)
    db.flush()
    return evidence


def _candidate_payload(product, evidence, **overrides):
    payload = {
        "product_id": product.product_id, "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id, "problem_id": "P17",
        "problem_type": "Problem/presentation",
        "problem_definition_ref": "SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        "relationship_role": "presentation", "relationship_status": "CANDIDATE",
        "feature_basis": "Evidence claim on visible dark-spot intensity; exact source is the selected Evidence record.",
        "outcome": "Change in visible dark-spot intensity; not a claim about cause or diagnosis.",
        "semantic_basis": "The manufacturer claim concerns visible dark spots and is a limited presentation-level candidate for P17 only.",
        "limitations": "Manufacturer-reported data on file; HBI SKU identity and variant are not verified; no cause-specific inference is permitted.",
        "decision_basis": "Identity is PARTIAL_IDENTITY and Evidence QA is PENDING; SUPPORTED and Recommendation are prohibited.",
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": "UNKNOWN", "market_region": "MEXICO",
        "reason": "Unit-test assessment rationale.",
        "idempotency_key": f"test-key-{evidence.evidence_id}-P17",
    }
    payload.update(overrides)
    return payload


def test_create_candidate_is_evidence_anchored_and_does_not_change_product_knowledge(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    link = ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, evidence))
    assert link.relationship_status == "CANDIDATE"
    assert link.revision_no == 1 and link.supersedes_link_id is None
    assert link.problem_id == "P17" and link.evidence_id == evidence.evidence_id
    assert db_session.query(ProductProblemLink).count() == 1
    assert db_session.query(ProductProblemLinkAssessmentEvent).count() == 1
    assert db_session.query(ProductProblemLinkAssessmentEvent).first().actor_id == "UNIT_TEST_ACTOR"
    assert db_session.query(ProductKnowledge).filter(ProductKnowledge.product_id == product.product_id).first() is None


def test_reassessment_is_append_only_and_preserves_previous_decision(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    first_payload = _candidate_payload(product, evidence)
    first = service.create_link(**first_payload)
    second_payload = _candidate_payload(
        product, evidence,
        relationship_status="DEFERRED",
        feature_basis="Evidence claim on visible dark-spot intensity; exact source is the selected Evidence record.",
        outcome="Change in visible dark-spot intensity; not a claim about cause or diagnosis.",
        reason="A reviewer deferred pending exact formula identity.",
        idempotency_key="test-key-revision-2",
    )
    second = service.reassess_link(
        first.link_id, expected_revision_no=1, actor_id="po-1",
        actor_role="PRODUCT_OWNER", **second_payload,
    )
    assert first.relationship_status == "CANDIDATE"
    assert second.relationship_status == "DEFERRED"
    assert second.revision_no == 2 and second.supersedes_link_id == first.link_id
    history = service.history(second.link_id)
    assert [r.revision_no for r in history["assessments"]] == [1, 2]
    assert len(history["events"]) == 2
    assert history["events"][1].before_state and history["events"][1].after_state


def test_idempotency_retry_returns_same_assessment_and_mismatch_conflicts(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    payload = _candidate_payload(product, evidence)
    first = service.create_link(**payload)
    retry = service.create_link(**payload)
    assert retry.link_id == first.link_id
    with pytest.raises(ConflictError, match="different request"):
        service.create_link(**{**payload, "outcome": "Changed outcome"})


def test_stale_revision_is_rejected(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    first = service.create_link(**_candidate_payload(product, evidence))
    second_payload = _candidate_payload(
        product, evidence, relationship_status="DEFERRED",
        idempotency_key="test-key-stale-rev-2", reason="Reassessment reason.",
    )
    service.reassess_link(first.link_id, expected_revision_no=1, actor_id="po-1",
                          actor_role="PRODUCT_OWNER", **second_payload)
    with pytest.raises(ConflictError, match="Stale assessment revision"):
        service.reassess_link(first.link_id, expected_revision_no=1, actor_id="po-1",
                              actor_role="PRODUCT_OWNER", **_candidate_payload(
                                  product, evidence, relationship_status="NOT_LINKED",
                                  idempotency_key="test-key-stale-rev-3",
                              ))


def test_supported_status_is_not_persistable(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    with pytest.raises(ValidationError, match="SUPPORTED is disabled"):
        ProductProblemLinkService(db_session).create_link(
            **_candidate_payload(product, evidence, relationship_status="SUPPORTED")
        )
    assert db_session.query(ProductProblemLink).count() == 0


def test_evidence_must_belong_to_the_same_product(db_session):
    product = _product(db_session)
    other = _product(db_session, product_id="PPL-PRODUCT-002")
    evidence = _evidence(db_session, other.product_id)
    with pytest.raises(ValidationError, match="same product"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, evidence))


def test_p22_cannot_receive_an_independent_product_problem_link(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        ProductProblemLinkService(db_session).create_link(
            **_candidate_payload(product, evidence, problem_id="P22")
        )


def test_unknown_problem_code_is_rejected(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    with pytest.raises(ValidationError, match="P01-P61"):
        ProductProblemLinkService(db_session).create_link(
            **_candidate_payload(product, evidence, problem_id="P99")
        )


def test_product_and_evidence_market_must_match_link_market(db_session):
    product = _product(db_session, market_region="EUROPE")
    evidence = _evidence(db_session, product.product_id, market_region="MEXICO")
    with pytest.raises(ValidationError, match="Product market"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, evidence))


def test_conflicted_or_rejected_evidence_cannot_anchor_a_link(db_session):
    product = _product(db_session)
    conflicted = _evidence(db_session, product.product_id, evidence_id="EV-PPL-CONFLICT",
                           claim_id="EV-PPL-CONFLICT-CLAIM", conflict_status="CONFLICT")
    with pytest.raises(ValidationError, match="Conflicted Evidence"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, conflicted))
    rejected = _evidence(db_session, product.product_id, evidence_id="EV-PPL-REJECTED",
                         claim_id="EV-PPL-REJECTED-CLAIM", qa_status="REJECTED")
    with pytest.raises(ValidationError, match="Rejected Evidence"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, rejected))
    assert db_session.query(ProductProblemLink).count() == 0


def test_market_and_semantic_fields_are_required(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    with pytest.raises(ValidationError, match="semantic_basis is required"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, evidence, semantic_basis=" "))
    with pytest.raises(ValidationError, match="market_region is required"):
        ProductProblemLinkService(db_session).create_link(**_candidate_payload(product, evidence, market_region=""))


def test_supported_status_is_blocked_by_database_constraint(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    db_session.commit()
    payload = _candidate_payload(product, evidence)
    payload.update({"link_id": "PPL-DIRECT-SUPPORTED", "relationship_status": "SUPPORTED"})
    payload.pop("reason")
    payload.pop("idempotency_key")
    with pytest.raises(IntegrityError):
        db_session.add(ProductProblemLink(**payload))
        db_session.flush()
    db_session.rollback()
    assert db_session.query(ProductProblemLink).count() == 0


def test_read_methods_return_links_by_product_problem_and_id(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    link = service.create_link(**_candidate_payload(product, evidence))
    repository = ProductProblemLinkRepository(db_session)
    assert service.list_by_product(product.product_id) == [link]
    assert service.list_by_problem("P17") == [link]
    assert repository.get_by_id(link.link_id) == link


def test_claim_id_and_map_version_are_validated(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    with pytest.raises(ValidationError, match="claim_id must exactly match"):
        service.create_link(**_candidate_payload(product, evidence, claim_id="EV-WRONG-CLAIM"))
    with pytest.raises(ValidationError, match="Unsupported problem_map_version"):
        service.create_link(**_candidate_payload(product, evidence, problem_map_version="SKIN_PROBLEM_SPACE_MAP_V9"))


def test_missing_product_or_evidence_is_rejected(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    payload = _candidate_payload(product, evidence)
    with pytest.raises(NotFoundError, match="Product MISSING"):
        service.create_link(**{**payload, "product_id": "MISSING"})
    with pytest.raises(NotFoundError, match="Evidence MISSING"):
        service.create_link(**{**payload, "evidence_id": "MISSING"})


def test_invalid_role_and_variant_are_rejected(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    with pytest.raises(ValidationError, match="Invalid relationship_role"):
        service.create_link(**_candidate_payload(product, evidence, relationship_role="diagnosis"))
    with pytest.raises(ValidationError, match="Invalid variant"):
        service.create_link(**_candidate_payload(product, evidence, variant="UNKNOWN_COLOR"))


def test_legacy_assessment_can_be_superseded_without_fabricated_old_revision(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    legacy = ProductProblemLink(
        link_id="PPL-LEGACY-ROW", product_id=product.product_id,
        variant="UNKNOWN", market_region="MEXICO", claim_id=evidence.claim_id,
        evidence_id=evidence.evidence_id, problem_id="P17",
        problem_type="Problem/presentation",
        problem_definition_ref="SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        relationship_role="presentation", relationship_status="NOT_LINKED",
        semantic_basis="Legacy semantic basis", limitations="Legacy limitations",
        decision_basis="Legacy decision", problem_map_version="SKIN_PROBLEM_SPACE_MAP_V0.1",
    )
    db_session.add(legacy)
    db_session.flush()
    revised = ProductProblemLinkService(db_session).reassess_link(
        legacy.link_id, expected_revision_no=None, actor_id="po-legacy",
        actor_role="PRODUCT_OWNER", **_candidate_payload(
            product, evidence, relationship_status="CANDIDATE",
            idempotency_key="legacy-successor-key-001",
            reason="New evidence interpretation after legacy assessment.",
        )
    )
    assert legacy.revision_no is None and legacy.assertion_key is None
    assert revised.revision_no == 1 and revised.supersedes_link_id == legacy.link_id
    history = ProductProblemLinkService(db_session).history(legacy.link_id)
    assert [item.link_id for item in history["assessments"]] == [legacy.link_id, revised.link_id]


def test_assessment_and_history_event_share_the_same_transaction(db_session):
    product = _product(db_session)
    evidence = _evidence(db_session, product.product_id)
    service = ProductProblemLinkService(db_session)
    service.create_link(**_candidate_payload(product, evidence))
    db_session.rollback()
    assert db_session.query(ProductProblemLink).count() == 0
    assert db_session.query(ProductProblemLinkAssessmentEvent).count() == 0
