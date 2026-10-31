from types import SimpleNamespace

from app.services.product_knowledge_service import ProductKnowledgeService


class FakeKnowledgeRepository:
    def __init__(self):
        self.knowledge = SimpleNamespace(
            product_knowledge_id="PK-P1",
            product_id="P1",
            ingredients="stale ingredient",
            ingredient_roles="stale role",
            claimed_benefits="stale benefit",
            known_use_cases="stale use case",
            contraindications="stale contraindication",
            usage_instructions="stale instruction",
            manufacturer_claims="stale claim",
            evidence_refs="stale-ref",
            evidence_status="SUPPORTED",
            knowledge_confidence=0.9,
        )

    def find_by_product(self, product_id):
        return self.knowledge

    def update_knowledge(self, product_id, **fields):
        for key, value in fields.items():
            setattr(self.knowledge, key, value)
        return self.knowledge


class FakeEvidenceRepository:
    def find_by_product(self, product_id):
        # No evidence is eligible for rebuilding: one is pending and one conflicts.
        return [
            SimpleNamespace(
                qa_status="PENDING",
                conflict_status="NONE",
                claim="pending claim",
                field="claimed_benefits",
                claim_id="pending-ref",
            ),
            SimpleNamespace(
                qa_status="APPROVED",
                conflict_status="CONFLICT",
                claim="conflicting claim",
                field="claimed_benefits",
                claim_id="conflict-ref",
            ),
        ]


def test_rebuild_clears_stale_status_and_fields_when_no_evidence_is_eligible():
    service = object.__new__(ProductKnowledgeService)
    service.repository = FakeKnowledgeRepository()
    service.evidence_repo = FakeEvidenceRepository()

    result = service.update_from_evidence("P1")

    assert result.evidence_status is None
    assert result.knowledge_confidence == 0.0
    assert result.ingredients is None
    assert result.claimed_benefits is None
    assert result.evidence_refs is None
