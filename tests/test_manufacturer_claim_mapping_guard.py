from types import SimpleNamespace

from app.services.product_knowledge_service import ProductKnowledgeService


def test_manufacturer_destination_requires_explicit_manufacturer_claim():
    rows = [
        SimpleNamespace(qa_status="APPROVED", conflict_status="NONE", field="manufacturer_claims", claim="marketing copy", claim_type="INFERENCE", claim_id="C1", evidence_strength="STRONG"),
        SimpleNamespace(qa_status="APPROVED", conflict_status="NONE", field="manufacturer_claims", claim="manufacturer statement", claim_type="MANUFACTURER_CLAIM", claim_id="C2", evidence_strength="STRONG"),
    ]
    captured = {}
    service = ProductKnowledgeService.__new__(ProductKnowledgeService)
    service.evidence_repo = SimpleNamespace(find_by_product=lambda product_id: rows)
    service.repository = SimpleNamespace(update_knowledge=lambda product_id, **data: captured.update(data) or SimpleNamespace(**data))
    service.get_or_create = lambda product_id: SimpleNamespace(product_id=product_id)

    service.update_from_evidence("TAXONOMY-003")

    assert captured["manufacturer_claims"] == "manufacturer statement"
