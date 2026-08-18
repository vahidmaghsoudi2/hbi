from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.repositories.product_knowledge_repository import ProductKnowledgeRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, ValidationError


class ProductKnowledgeService(BaseService[ProductKnowledge, ProductKnowledgeRepository]):
    def __init__(self, db: Session):
        super().__init__(ProductKnowledgeRepository(db), db)
        self.evidence_repo = EvidenceRepository(db)

    def get_or_create(self, product_id: str) -> ProductKnowledge:
        knowledge = self.repository.find_by_product(product_id)
        if not knowledge:
            knowledge = self.repository.create(
                product_knowledge_id=f"PK-{product_id}",
                product_id=product_id
            )
        return knowledge

    def update_from_evidence(self, product_id: str) -> ProductKnowledge:
        knowledge = self.get_or_create(product_id)
        evidences = self.evidence_repo.find_by_product(product_id)

        ingredients = set()
        benefits = set()
        use_cases = set()
        contraindications = set()
        evidence_refs = []

        for ev in evidences:
            claim = ev.claim or ""
            if ev.field == "ingredients" and claim:
                ingredients.update([i.strip() for i in claim.split(",")])
            elif ev.field in ("claimed_benefits", "benefit") and claim:
                benefits.update([b.strip() for b in claim.split(",")])
            elif ev.field in ("known_use_cases", "use_case") and claim:
                use_cases.update([u.strip() for u in claim.split(",")])
            elif ev.field == "contraindications" and claim:
                contraindications.update([c.strip() for c in claim.split(",")])
            if ev.claim_id:
                evidence_refs.append(ev.claim_id)

        update_data = {
            "ingredients": ", ".join(ingredients) if ingredients else None,
            "claimed_benefits": ", ".join(benefits) if benefits else None,
            "known_use_cases": ", ".join(use_cases) if use_cases else None,
            "contraindications": ", ".join(contraindications) if contraindications else None,
            "evidence_refs": ", ".join(evidence_refs) if evidence_refs else None,
        }

        confidence = self._calculate_confidence_from_evidences(evidences)
        update_data["knowledge_confidence"] = confidence

        updated = self.repository.update_knowledge(product_id, **update_data)
        if not updated:
            updated = self.repository.create(
                product_knowledge_id=f"PK-{product_id}",
                product_id=product_id,
                **update_data
            )
        return updated

    def _calculate_confidence_from_evidences(self, evidences: List[Evidence]) -> float:
        if not evidences:
            return 0.0

        strength_map = {
            "STRONG": 0.9,
            "MODERATE": 0.6,
            "WEAK": 0.3,
            "UNVERIFIED": 0.1
        }

        total_weight = 0.0
        count = 0
        for ev in evidences:
            strength = ev.evidence_strength or "UNVERIFIED"
            weight = strength_map.get(strength, 0.1)
            total_weight += weight
            count += 1

        avg = total_weight / count if count > 0 else 0.0
        return round(avg, 2)
