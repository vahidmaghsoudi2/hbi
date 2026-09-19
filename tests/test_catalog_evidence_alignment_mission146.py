"""Mission #146 — Evidence / ProductKnowledge / Need alignment locks.

Freezes repository-grounded behavior for D3 (Evidence acceptance for readiness)
and D4 (ProductKnowledge known_use_cases ↔ engine Need vocabulary).
Does not promote seed, change scoring, or invent policy.
"""
from __future__ import annotations

from app.models.evidence import Evidence
from app.models.product import Product
from app.services.evidence_readiness_service import EvidenceReadinessService
from app.services.need_normalization import CANONICAL_NEEDS, normalize_needs_from_factors
from app.services.product_compatibility import product_compatibility_ids
from app.services.recommendation_service import NEED_MATCH_SUFFICIENT


# Seed categories from data/seed_products.json (exact strings used as known_use_cases).
SEED_CATEGORY_TO_NEEDS = {
    "ضدآفتاب ضدلک صورت": {"sun_protection", "brightening"},
    "ضدآفتاب رنگی ضدلک صورت": {"sun_protection", "brightening"},
    "ضدآفتاب روزانه صورت": {"sun_protection"},
    "کرم روزانه ضدپیری صورت": {"anti_aging"},
}


def test_d4_seed_categories_map_to_canonical_need_ids():
    for category, expected in SEED_CATEGORY_TO_NEEDS.items():
        assert set(product_compatibility_ids(category)) == expected


def test_d4_customer_sunscreen_need_matches_seed_spf_category():
    factors = [
        {"name": "concern", "value": "ضدآفتاب", "source": "customer_input", "validity": "DECLARED"}
    ]
    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(factors)
    assert unmapped == []
    assert ambiguous == []
    assert needs == ["sun protection"]
    surface_to_id = {surface: cid for cid, surface in CANONICAL_NEEDS.items()}
    generated_ids = {surface_to_id[n] for n in needs if n in surface_to_id}
    product_ids = set(product_compatibility_ids("ضدآفتاب روزانه صورت"))
    match = len(generated_ids & product_ids) / max(len(generated_ids), 1)
    assert match >= NEED_MATCH_SUFFICIENT
    assert match == 1.0


def test_d4_unlisted_product_phrase_does_not_guess_need_ids():
    # Unknown product-side phrase must not invent compatibility (GAP-05 rule).
    assert product_compatibility_ids("فرمول اختصاصی گالری ناشناس") == []


def test_d3_pending_evidence_blocks_readiness(db_session):
    pid = "P_M146_EV_PENDING"
    db_session.add(
        Product(
            product_id=pid,
            brand="M146",
            product_name="Pending Evidence Product",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="QA_REVIEW",
        )
    )
    db_session.add(
        Evidence(
            evidence_id=f"EV-{pid}-1",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="SECONDARY",
            source_reference="seed://brand",
            claim="brand is M146",
            field="brand",
            claim_type="FACT",
            qa_status="PENDING",
            conflict_status="NONE",
        )
    )
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate(pid)
    assert result.ready is False
    assert f"EV-{pid}-1" in result.incomplete_qa_evidence_ids


def test_d3_approved_identity_evidence_can_pass_readiness_alone(db_session):
    """Model supports readiness with APPROVED evidence even if claim is identity-level.

    Whether identity-only evidence is *sufficient policy* for Product QA VALID
    remains PO_DECISION_REQUIRED (D3 quality bar) — this test only locks code behavior.
    """
    pid = "P_M146_EV_APPROVED_ID"
    db_session.add(
        Product(
            product_id=pid,
            brand="M146",
            product_name="Approved Identity Evidence Product",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="QA_REVIEW",
        )
    )
    db_session.add(
        Evidence(
            evidence_id=f"EV-{pid}-1",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="SECONDARY",
            source_reference="docs/product_record",
            claim="brand is M146",
            field="brand",
            claim_type="FACT",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate(pid)
    assert result.ready is True, result.summary


def test_d3_mixed_approved_and_pending_still_blocks(db_session):
    pid = "P_M146_EV_MIXED"
    db_session.add(
        Product(
            product_id=pid,
            brand="M146",
            product_name="Mixed Evidence Product",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="QA_REVIEW",
        )
    )
    db_session.add_all(
        [
            Evidence(
                evidence_id=f"EV-{pid}-OK",
                product_id=pid,
                claim_id=f"EV-{pid}-001",
                source_type="PEER_REVIEWED",
                source_reference="test://ok",
                claim="supports sun protection",
                field="known_use_cases",
                claim_type="BENEFIT",
                qa_status="APPROVED",
                conflict_status="NONE",
            ),
            Evidence(
                evidence_id=f"EV-{pid}-PEND",
                product_id=pid,
                claim_id=f"EV-{pid}-002",
                source_type="SECONDARY",
                source_reference="seed://name",
                claim="canonical name",
                field="product_name",
                claim_type="FACT",
                qa_status="PENDING",
                conflict_status="NONE",
            ),
        ]
    )
    db_session.flush()
    result = EvidenceReadinessService(db_session).evaluate(pid)
    assert result.ready is False
    assert f"EV-{pid}-PEND" in result.incomplete_qa_evidence_ids


def test_d4_canonical_need_ids_cover_home_relevant_surfaces():
    # Surfaces the engine vocabulary actually defines (not invented).
    expected_ids = {
        "hydration",
        "barrier_repair",
        "dry_skin",
        "oil_control",
        "acne_care",
        "sensitivity",
        "sun_protection",
        "brightening",
        "anti_aging",
        "cleansing",
    }
    assert expected_ids.issubset(set(CANONICAL_NEEDS.keys()))
