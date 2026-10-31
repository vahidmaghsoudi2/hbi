import pytest
from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_problem_link import ProductProblemLink
from app.services.product_problem_link_service import ProductProblemLinkService


def _p5_product(db):
    product = Product(product_id="P5-ISDIN-ISOLATED-TEST", brand="ISDIN",
                      product_name="FotoUltra 100 Active Unify SPF50+",
                      identity_status="PARTIAL_IDENTITY", qa_verdict="PENDING",
                      status="DRAFT", market_region="UNKNOWN")
    db.add(product); db.flush()
    return product


def _p5_evidence(db, product_id, *, evidence_id, claim_id, market_region, claim):
    evidence = Evidence(evidence_id=evidence_id, product_id=product_id, claim_id=claim_id,
                        source_type="MANUFACTURER",
                        source_reference=f"ISDIN manufacturer claim; {market_region}; Data on file / regional product page",
                        claim=claim, field="claim", market_region=market_region,
                        claim_type="MANUFACTURER_CLAIM", evidence_status="UNKNOWN",
                        evidence_strength="UNVERIFIED", qa_status="PENDING", conflict_status="NONE")
    db.add(evidence); db.flush()
    return evidence


def _link_payload(product, evidence, *, problem_id, role, status, semantic_basis, limitations, decision_basis):
    return {
        "product_id": product.product_id, "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id, "problem_id": problem_id,
        "problem_type": {"P17":"Problem/presentation","P18":"Clinical Condition",
                         "P19":"Sequela/pigmentation presentation","P22":"Context/pigmentation presentation",
                         "P08":"Problem/Clinical presentation","P24":"Problem/presentation"}[problem_id],
        "problem_definition_ref": f"SKIN_PROBLEM_SPACE_MAP_V0.1.md#{problem_id}",
        "relationship_role": role, "relationship_status": status,
        "feature_basis": f"Selected manufacturer Evidence claim: {evidence.claim}",
        "outcome": "Manufacturer-reported outcome limited to the stated endpoint; no diagnosis or recommendation.",
        "semantic_basis": semantic_basis, "limitations": limitations,
        "decision_basis": decision_basis, "reason": "P5 isolated boundary test.",
        "idempotency_key": f"p5-test-key-{evidence.evidence_id}-{problem_id}",
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": "UNKNOWN", "market_region": evidence.market_region,
    }


def test_p5_mexico_dark_spot_claim_is_only_a_p17_candidate(db_session):
    product = _p5_product(db_session)
    evidence = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-MX-22-15-TEST",
                            claim_id="P5-CLAIM-MX-22-15-TEST", market_region="MEXICO",
                            claim="Manufacturer-reported assessment in 31 participants: 22% reduction in spot intensity and 15% reduction in spot area; Data on file (2024).")
    link = ProductProblemLinkService(db_session).create_link(**_link_payload(
        product, evidence, problem_id="P17", role="presentation", status="CANDIDATE",
        semantic_basis="Visible dark spots support a limited presentation-level candidate for P17 only.",
        limitations="Manufacturer-reported Data on file; exact SKU and variant are not verified; no cause-specific inference.",
        decision_basis="P17 is descriptive; Evidence QA pending; no SUPPORTED or Recommendation.",
    ))
    assert link.relationship_status == "CANDIDATE" and link.problem_id == "P17"
    assert link.market_region == "MEXICO" and link.revision_no == 1
    assert product.status == "DRAFT" and product.identity_status == "PARTIAL_IDENTITY"
    assert product.qa_verdict == "PENDING"
    assert db_session.query(ProductKnowledge).filter(ProductKnowledge.product_id == product.product_id).first() is None
    assert db_session.query(ProductProblemLink).count() == 1


def test_p5_boundary_assessments_remain_not_linked_and_separate(db_session):
    product = _p5_product(db_session)
    melasma = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-SA-MASI-TEST",
                            claim_id="P5-CLAIM-SA-MASI-TEST", market_region="SOUTH_AFRICA",
                            claim="Manufacturer regional page reports a 25% MASI change; public study protocol unavailable.")
    pih = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-SA-PIH-MENTION-TEST",
                       claim_id="P5-CLAIM-SA-PIH-MENTION-TEST", market_region="SOUTH_AFRICA",
                       claim="Regional product information mentions PIH generally; no product-specific PIH outcome study.")
    service = ProductProblemLinkService(db_session)
    p18 = service.create_link(**_link_payload(
        product, melasma, problem_id="P18", role="clinical_anchor", status="NOT_LINKED",
        semantic_basis="MASI statement retained for boundary review only.",
        limitations="Public study design and protocol unavailable; no treatment efficacy or recommendation.",
        decision_basis="Evidence insufficient for a product recommendation link; P18 remains a clinical anchor.",
    ))
    p19 = service.create_link(**_link_payload(
        product, pih, problem_id="P19", role="sequela", status="NOT_LINKED",
        semantic_basis="A general PIH mention is not a product-specific PIH outcome.",
        limitations="No dedicated product-specific PIH study; P19 remains distinct from P17.",
        decision_basis="Available claim does not establish a P5-to-P19 product relationship.",
    ))
    assert p18.relationship_status == "NOT_LINKED" and p18.relationship_role == "clinical_anchor"
    assert p19.relationship_status == "NOT_LINKED" and p19.relationship_role == "sequela"
    assert {r.problem_id for r in service.list_by_product(product.product_id)} == {"P18", "P19"}
    assert product.status == "DRAFT"
    assert db_session.query(ProductKnowledge).filter(ProductKnowledge.product_id == product.product_id).first() is None


def test_p5_p22_context_cannot_be_an_independent_link(db_session):
    product = _p5_product(db_session)
    evidence = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-MX-SUN-CONTEXT-TEST",
                            claim_id="P5-CLAIM-MX-SUN-CONTEXT-TEST", market_region="MEXICO",
                            claim="Manufacturer describes sun-related dark-spot claims and UV protection.")
    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        ProductProblemLinkService(db_session).create_link(**_link_payload(
            product, evidence, problem_id="P22", role="context", status="DEFERRED",
            semantic_basis="P22 is context only.", limitations="Not an independent destination.",
            decision_basis="Owner-designated Map defines P22 as context/reference only.",
        ))
    assert db_session.query(ProductProblemLink).count() == 0


def test_p5_non_comedogenic_and_uv_claims_do_not_link_acne_or_persistent_redness(db_session):
    product = _p5_product(db_session)
    non_comedogenic = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-MX-NON-COMEDOGENIC-TEST",
                                   claim_id="P5-CLAIM-MX-NON-COMEDOGENIC-TEST", market_region="MEXICO",
                                   claim="Non-comedogenic positioning; no acne treatment outcome supplied.")
    uv = _p5_evidence(db_session, product.product_id, evidence_id="P5-EV-MX-UV-REDNESS-TEST",
                      claim_id="P5-CLAIM-MX-UV-REDNESS-TEST", market_region="MEXICO",
                      claim="UV protection; no persistent-redness or rosacea outcome supplied.")
    service = ProductProblemLinkService(db_session)
    p08 = service.create_link(**_link_payload(
        product, non_comedogenic, problem_id="P08", role="presentation", status="NOT_LINKED",
        semantic_basis="Non-comedogenic positioning is not an acne treatment outcome.",
        limitations="No product-specific acne treatment evidence supplied.",
        decision_basis="No supported product-to-acne relationship.",
    ))
    p24 = service.create_link(**_link_payload(
        product, uv, problem_id="P24", role="presentation", status="NOT_LINKED",
        semantic_basis="UV protection does not establish reduction in persistent redness.",
        limitations="No product-specific persistent-redness outcome supplied.",
        decision_basis="Sunscreen positioning cannot fill the evidence gap.",
    ))
    assert p08.problem_id == "P08" and p08.relationship_status == "NOT_LINKED"
    assert p24.problem_id == "P24" and p24.relationship_status == "NOT_LINKED"
    assert {r.problem_id for r in service.list_by_product(product.product_id)} == {"P08", "P24"}
    assert product.status == "DRAFT" and product.identity_status == "PARTIAL_IDENTITY"
