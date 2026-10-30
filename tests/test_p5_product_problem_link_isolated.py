import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_problem_link import ProductProblemLink
from app.services.product_problem_link_service import ProductProblemLinkService


def _p5_product(db):
    product = Product(
        product_id="P5-ISDIN-ISOLATED-TEST",
        brand="ISDIN",
        product_name="FotoUltra 100 Active Unify SPF50+",
        identity_status="PARTIAL_IDENTITY",
        qa_verdict="PENDING",
        status="DRAFT",
        market_region="UNKNOWN",
    )
    db.add(product)
    db.flush()
    return product


def _p5_evidence(
    db,
    product_id,
    *,
    evidence_id,
    claim_id,
    market_region,
    claim,
):
    evidence = Evidence(
        evidence_id=evidence_id,
        product_id=product_id,
        claim_id=claim_id,
        source_type="MANUFACTURER",
        source_reference=f"ISDIN manufacturer claim; {market_region}; Data on file / regional product page",
        claim=claim,
        field="claim",
        market_region=market_region,
        claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN",
        evidence_strength="UNVERIFIED",
        qa_status="PENDING",
        conflict_status="NONE",
    )
    db.add(evidence)
    db.flush()
    return evidence


def _link_payload(product, evidence, *, problem_id, role, status, semantic_basis, limitations, decision_basis):
    return {
        "product_id": product.product_id,
        "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id,
        "problem_id": problem_id,
        "problem_type": {
            "P17": "Problem/presentation",
            "P18": "Clinical Condition",
            "P19": "Sequela/pigmentation presentation",
            "P22": "Context/pigmentation presentation",
            "P08": "Problem/Clinical presentation",
            "P24": "Problem/presentation",
        }[problem_id],
        "problem_definition_ref": f"SKIN_PROBLEM_SPACE_MAP_V0.1.md#{problem_id}",
        "relationship_role": role,
        "relationship_status": status,
        "semantic_basis": semantic_basis,
        "limitations": limitations,
        "decision_basis": decision_basis,
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": "UNKNOWN",
        "market_region": evidence.market_region,
    }


def test_p5_mexico_dark_spot_claim_is_only_a_p17_candidate(db_session):
    product = _p5_product(db_session)
    evidence = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-MX-22-15-TEST",
        claim_id="P5-CLAIM-MX-22-15-TEST",
        market_region="MEXICO",
        claim=(
            "Manufacturer-reported assessment in 31 participants: "
            "22% reduction in spot intensity and 15% reduction in spot area; "
            "Data on file (2024)."
        ),
    )

    service = ProductProblemLinkService(db_session)
    link = service.create_link(**_link_payload(
        product,
        evidence,
        problem_id="P17",
        role="presentation",
        status="CANDIDATE",
        semantic_basis=(
            "The manufacturer claim concerns visible dark spots and supports "
            "a limited presentation-level semantic candidate for P17 only."
        ),
        limitations=(
            "Manufacturer-reported Data on file; full public protocol is unavailable; "
            "HBI SKU, market, physical package, and variant are not verified; "
            "no cause-specific inference is permitted."
        ),
        decision_basis=(
            "P17 is a descriptive presentation layer with Accepted=No and "
            "Operational=Undetermined. Evidence QA is PENDING and evidence status "
            "is UNKNOWN; SUPPORTED and Recommendation are prohibited."
        ),
    ))

    assert link.relationship_status == "CANDIDATE"
    assert link.problem_id == "P17"
    assert link.market_region == "MEXICO"
    assert product.status == "DRAFT"
    assert product.identity_status == "PARTIAL_IDENTITY"
    assert product.qa_verdict == "PENDING"
    assert db_session.query(ProductKnowledge).filter(
        ProductKnowledge.product_id == product.product_id
    ).first() is None
    assert db_session.query(ProductProblemLink).count() == 1


def test_p5_melasma_and_pih_claims_are_not_linked_as_recommendation_relations(db_session):
    product = _p5_product(db_session)
    melasma = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-SA-MASI-TEST",
        claim_id="P5-CLAIM-SA-MASI-TEST",
        market_region="SOUTH_AFRICA",
        claim="Manufacturer regional page reports a 25% MASI change; public study protocol is unavailable.",
    )
    pih = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-SA-PIH-MENTION-TEST",
        claim_id="P5-CLAIM-SA-PIH-MENTION-TEST",
        market_region="SOUTH_AFRICA",
        claim="Regional product information mentions PIH generally; no product-specific PIH outcome study is supplied.",
    )

    service = ProductProblemLinkService(db_session)
    p18 = service.create_link(**_link_payload(
        product,
        melasma,
        problem_id="P18",
        role="clinical_anchor",
        status="NOT_LINKED",
        semantic_basis=(
            "The MASI statement is retained for boundary review only; "
            "P18 remains a Clinical Anchor and is not a routine-care target."
        ),
        limitations=(
            "Public study design and protocol are unavailable; this record "
            "does not establish treatment efficacy or recommendation suitability."
        ),
        decision_basis=(
            "The current evidence is insufficient for a product recommendation link; "
            "P18 remains a Clinical Anchor."
        ),
    ))
    p19 = service.create_link(**_link_payload(
        product,
        pih,
        problem_id="P19",
        role="sequela",
        status="NOT_LINKED",
        semantic_basis=(
            "A general PIH mention is not a product-specific PIH outcome."
        ),
        limitations=(
            "No dedicated product-specific PIH study is supplied; P19 remains "
            "distinct from P17 and is not inferred from ingredient hypotheses."
        ),
        decision_basis=(
            "The available claim does not establish a P5-to-P19 product relationship."
        ),
    ))

    assert p18.relationship_status == "NOT_LINKED"
    assert p18.relationship_role == "clinical_anchor"
    assert p19.relationship_status == "NOT_LINKED"
    assert p19.relationship_role == "sequela"
    assert {row.problem_id for row in service.list_by_product(product.product_id)} == {"P18", "P19"}
    assert product.status == "DRAFT"
    assert db_session.query(ProductKnowledge).filter(
        ProductKnowledge.product_id == product.product_id
    ).first() is None


def test_p5_sun_related_pigmentation_cannot_be_created_as_independent_p22_link(db_session):
    product = _p5_product(db_session)
    evidence = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-MX-SUN-CONTEXT-TEST",
        claim_id="P5-CLAIM-MX-SUN-CONTEXT-TEST",
        market_region="MEXICO",
        claim="Manufacturer describes sun-related dark-spot claims and UV protection.",
    )

    service = ProductProblemLinkService(db_session)
    payload = _link_payload(
        product,
        evidence,
        problem_id="P22",
        role="context",
        status="DEFERRED",
        semantic_basis="P22 is retained only as context under the canonical Map.",
        limitations="P22 is not an independent ProductProblemLink destination.",
        decision_basis="The owner-designated Map classifies P22 as Context/reference only.",
    )

    with pytest.raises(ValidationError, match="P22 is Context/reference only"):
        service.create_link(**payload)

    assert db_session.query(ProductProblemLink).count() == 0
    assert product.status == "DRAFT"



def test_p5_non_comedogenic_and_uv_claims_do_not_link_acne_or_persistent_redness(db_session):
    product = _p5_product(db_session)
    non_comedogenic = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-MX-NON-COMEDOGENIC-TEST",
        claim_id="P5-CLAIM-MX-NON-COMEDOGENIC-TEST",
        market_region="MEXICO",
        claim="Manufacturer product information describes the product as non-comedogenic; no acne treatment outcome is supplied.",
    )
    uv_protection = _p5_evidence(
        db_session,
        product.product_id,
        evidence_id="P5-EV-MX-UV-REDNESS-TEST",
        claim_id="P5-CLAIM-MX-UV-REDNESS-TEST",
        market_region="MEXICO",
        claim="Manufacturer product information describes UV protection; no persistent-redness or rosacea outcome is supplied.",
    )

    service = ProductProblemLinkService(db_session)
    p08 = service.create_link(**_link_payload(
        product,
        non_comedogenic,
        problem_id="P08",
        role="presentation",
        status="NOT_LINKED",
        semantic_basis=(
            "Non-comedogenic positioning is not an acne treatment outcome and "
            "does not establish a product-to-acne relationship."
        ),
        limitations=(
            "No product-specific acne treatment evidence is supplied; P08 remains "
            "Accepted=No and Operational=Undetermined."
        ),
        decision_basis=(
            "The canonical P5 assessment explicitly rejects non-comedogenic "
            "wording as a basis for an acne-treatment link."
        ),
    ))
    p24 = service.create_link(**_link_payload(
        product,
        uv_protection,
        problem_id="P24",
        role="presentation",
        status="NOT_LINKED",
        semantic_basis=(
            "UV protection does not establish a reduction in persistent redness."
        ),
        limitations=(
            "No product-specific persistent-redness outcome is supplied; P24 "
            "remains Accepted=No and Operational=Undetermined."
        ),
        decision_basis=(
            "The canonical P5 assessment finds no specific evidence for persistent "
            "redness; sunscreen positioning cannot fill that evidence gap."
        ),
    ))

    assert p08.relationship_status == "NOT_LINKED"
    assert p08.problem_id == "P08"
    assert p24.relationship_status == "NOT_LINKED"
    assert p24.problem_id == "P24"
    assert {
        row.problem_id for row in service.list_by_product(product.product_id)
    } == {"P08", "P24"}
    assert product.status == "DRAFT"
    assert product.identity_status == "PARTIAL_IDENTITY"
    assert product.qa_verdict == "PENDING"
    assert db_session.query(ProductKnowledge).filter(
        ProductKnowledge.product_id == product.product_id
    ).first() is None
