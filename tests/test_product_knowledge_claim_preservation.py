from types import SimpleNamespace

from app.services.product_knowledge_service import ProductKnowledgeService, _join_claims


def test_join_claims_preserves_commas_and_complete_sentences():
    first = "The manufacturer reports +162.5% deep moisture, based on 20 subjects."
    second = "Full protocol, comparator, and independent replication were not available."

    assert _join_claims({first, second}) == "\n".join(sorted([first, second]))


def test_join_claims_deduplicates_without_splitting_claims():
    claim = "Skin conditioning, moisture, texture, and radiance claims."
    assert _join_claims({claim, claim}) == claim
    assert _join_claims(set()) is None


def test_update_from_evidence_keeps_free_text_claims_intact():
    product_id = "HBI-TEST-COSRX"
    ingredients = (
        "The official page lists Acetyl Hexapeptide-8, Copper Tripeptide-1, "
        "and niacinamide, hyaluronic acid, and allantoin."
    )
    use_case = (
        "Manufacturer positioning: skin conditioning/booster use with moisture, "
        "texture and radiance claims. These are cosmetic statements."
    )
    manufacturer_claim = (
        "The manufacturer reports +162.5% deep moisture, +76.4% texture, "
        "and +40.1% clarity based on 20 subjects."
    )
    second_manufacturer_claim = (
        "The reported study ran from 2023-09-18 to 2023-10-31, "
        "with full protocol, comparator, and analysis unavailable."
    )

    evidence = [
        SimpleNamespace(
            product_id=product_id,
            field="ingredients",
            claim=ingredients,
            qa_status="VERIFIED",
            conflict_status="NONE",
            market_region=None,
            packaging_version=None,
            claim_type="MANUFACTURER_CLAIM",
            claim_id="claim-001",
            evidence_strength="STRONG",
        ),
        SimpleNamespace(
            product_id=product_id,
            field="known_use_cases",
            claim=use_case,
            qa_status="VERIFIED",
            conflict_status="NONE",
            market_region=None,
            packaging_version=None,
            claim_type="MANUFACTURER_CLAIM",
            claim_id="claim-002",
            evidence_strength="STRONG",
        ),
        SimpleNamespace(
            product_id=product_id,
            field="manufacturer_claims",
            claim=manufacturer_claim,
            qa_status="VERIFIED",
            conflict_status="NONE",
            market_region=None,
            packaging_version=None,
            claim_type="MANUFACTURER_CLAIM",
            claim_id="claim-003",
            evidence_strength="STRONG",
        ),
        SimpleNamespace(
            product_id=product_id,
            field="manufacturer_claims",
            claim=second_manufacturer_claim,
            qa_status="VERIFIED",
            conflict_status="NONE",
            market_region=None,
            packaging_version=None,
            claim_type="MANUFACTURER_CLAIM",
            claim_id="claim-004",
            evidence_strength="STRONG",
        ),
    ]

    class EvidenceRepo:
        def find_by_product(self, requested_product_id):
            assert requested_product_id == product_id
            return evidence

    class KnowledgeRepo:
        def update_knowledge(self, requested_product_id, **values):
            assert requested_product_id == product_id
            self.values = values
            return values

    service = ProductKnowledgeService.__new__(ProductKnowledgeService)
    service.db = None
    service.evidence_repo = EvidenceRepo()
    service.repository = KnowledgeRepo()
    service.get_or_create = lambda requested_product_id: object()

    result = service.update_from_evidence(product_id)

    assert result["ingredients"] == ingredients
    assert result["known_use_cases"] == use_case
    assert result["manufacturer_claims"] == "\n".join(
        sorted([manufacturer_claim, second_manufacturer_claim])
    )
    assert "evidence-001" not in result["evidence_refs"]
    assert result["evidence_refs"] == "claim-001, claim-002, claim-003, claim-004"
