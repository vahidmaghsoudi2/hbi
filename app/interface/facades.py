from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.services.product_service import ProductService
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.recommendation_service import RecommendationService
from app.services.inventory_service import InventoryService
from app.services.sale_service import SaleService
from app.interface.dto import (
    ProductDTO, CustomerDTO, CaseDTO, RecommendationDTO,
    InventoryDTO, SaleDTO, SaleItemDTO
)
from app.interface.errors import NotFoundError, ValidationError, BusinessRuleError

def _to_product_dto(p) -> ProductDTO:
    return ProductDTO(
        product_id=p.product_id,
        brand=p.brand,
        product_name=p.product_name,
        identity_status=p.identity_status,
        qa_verdict=p.qa_verdict,
        variant=p.variant,
        size_value=p.size_value,
        size_unit=p.size_unit
    )

def _to_customer_dto(c) -> CustomerDTO:
    return CustomerDTO(
        customer_id=c.customer_id,
        name=c.name,
        mobile=c.mobile,
        consent_to_store_data=c.consent_to_store_data
    )

def _to_case_dto(c) -> CaseDTO:
    return CaseDTO(
        case_id=c.case_id,
        customer_id=c.customer_id,
        case_type=c.case_type
    )


def _get_availability(db: Session, product_id: str) -> str:
    try:
        from app.models.inventory import Inventory
        inv = db.query(Inventory).filter_by(product_id=product_id).first()
        if not inv:
            return "OUT_OF_STOCK"
        return "AVAILABLE" if inv.quantity_available > 0 else "OUT_OF_STOCK"
    except Exception:
        return "UNKNOWN"


def _get_price(db: Session, product_id: str):
    try:
        from app.models.inventory import Inventory
        inv = db.query(Inventory).filter_by(product_id=product_id).first()
        return inv.sale_price_toman if inv else None
    except Exception:
        return None


def _to_recommendation_dto(r, db: Session) -> RecommendationDTO:
    """Map Recommendation model to DTO with AD-3 Contract fields."""
    need = r.need_match_score or 0.0
    ev = getattr(r, 'evidence_score', None) or 0.0
    confidence = round(min(1.0, 0.4 * need + 0.6 * ev), 2)

    return RecommendationDTO(
        recommendation_id=r.recommendation_id,
        case_id=r.case_id,
        product_id=r.product_id,
        need_match_score=r.need_match_score,
        eligibility_status=r.eligibility_status,
        ranking_score=r.ranking_score,
        ranking_reasons=r.ranking_reasons,
        final_score=r.ranking_score,
        confidence=confidence,
        eligibility=r.eligibility_status,
        reasoning=r.ranking_reasons,
        evidence_score=getattr(r, 'evidence_score', None),
        evidence_refs=[],
        warnings=[],
        availability=_get_availability(db, r.product_id),
        price=_get_price(db, r.product_id),
    )

def _to_inventory_dto(i) -> InventoryDTO:
    return InventoryDTO(
        inventory_id=i.inventory_id,
        product_id=i.product_id,
        quantity_available=i.quantity_available,
        quantity_reserved=i.quantity_reserved,
        stock_status=i.stock_status,
        sale_price_toman=i.sale_price_toman
    )

class ProductFacade:
    def __init__(self, db: Session):
        self.service = ProductService(db)

    def get_by_id(self, product_id: str) -> ProductDTO:
        product = self.service.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        return _to_product_dto(product)

    def find_by_brand(self, brand: str) -> List[ProductDTO]:
        products = self.service.find_by_brand(brand)
        return [_to_product_dto(p) for p in products]

    def get_verified_products(self) -> List[ProductDTO]:
        products = self.service.get_verified_products()
        return [_to_product_dto(p) for p in products]

class CustomerFacade:
    def __init__(self, db: Session):
        self.service = CustomerService(db)

    def register(self, name: str, mobile: Optional[str] = None, consent: int = 0) -> CustomerDTO:
        try:
            customer = self.service.register_customer(
                name=name,
                mobile=mobile,
                consent_to_store_data=consent
            )
            return _to_customer_dto(customer)
        except ValueError as e:
            raise BusinessRuleError(str(e))

    def find_by_mobile(self, mobile: str) -> CustomerDTO:
        customer = self.service.find_by_mobile(mobile)
        if not customer:
            raise NotFoundError(f"Customer with mobile {mobile} not found")
        return _to_customer_dto(customer)

class CaseFacade:
    def __init__(self, db: Session):
        self.service = CaseService(db)

    def create(self, customer_id: str, case_type: str = "OPEN") -> CaseDTO:
        case = self.service.create_case(customer_id=customer_id, case_type=case_type)
        return _to_case_dto(case)

    def find_by_customer(self, customer_id: str) -> List[CaseDTO]:
        cases = self.service.find_by_customer(customer_id)
        return [_to_case_dto(c) for c in cases]

    def close(self, case_id: str) -> CaseDTO:
        case = self.service.close_case(case_id)
        if not case:
            raise NotFoundError(f"Case {case_id} not found")
        return _to_case_dto(case)

class RecommendationFacade:
    def __init__(self, db: Session):
        self.db = db
        self.service = RecommendationService(db)

    def generate(self, case_id: str, customer_profile: Dict) -> List[RecommendationDTO]:
        recommendations = self.service.generate_recommendations(case_id, customer_profile or {})
        return [_to_recommendation_dto(r, self.db) for r in recommendations]

    def find_by_case(self, case_id: str) -> List[RecommendationDTO]:
        recommendations = self.service.find_by_case(case_id)
        return [_to_recommendation_dto(r, self.db) for r in recommendations]

class InventoryFacade:
    def __init__(self, db: Session):
        self.service = InventoryService(db)

    def get_by_product(self, product_id: str) -> InventoryDTO:
        inventory = self.service.find_by_product(product_id)
        if not inventory:
            raise NotFoundError(f"Inventory for product {product_id} not found")
        return _to_inventory_dto(inventory)

    def find_available(self) -> List[InventoryDTO]:
        items = self.service.find_available()
        return [_to_inventory_dto(i) for i in items]

class SaleFacade:
    def __init__(self, db: Session):
        self.service = SaleService(db)

    def create_sale(self, customer_id: str, items: List[Dict]) -> SaleDTO:
        try:
            sale = self.service.create_sale(customer_id, items)
            sale_items = self.service.get_sale_items(sale.sale_id)
            item_dtos = [
                SaleItemDTO(
                    sale_item_id=si.sale_item_id,
                    sale_id=si.sale_id,
                    product_id=si.product_id,
                    quantity=si.quantity,
                    unit_price_toman=si.unit_price_toman
                ) for si in sale_items
            ]
            return SaleDTO(
                sale_id=sale.sale_id,
                customer_id=sale.customer_id,
                total_amount_toman=sale.total_amount_toman,
                items=item_dtos
            )
        except ValueError as e:
            raise BusinessRuleError(str(e))

    def get_total_sales(self) -> int:
        return self.service.get_total_sales()

from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService
from app.interface.dto import EvidenceDTO, ProductKnowledgeDTO, ConflictEntryDTO


class EvidenceFacade:
    def __init__(self, db: Session):
        self.db = db
        self.service = EvidenceService(db)

    def add_evidence(self, evidence_data: Dict) -> EvidenceDTO:
        evidence = self.service.add_evidence(evidence_data)
        return self._to_evidence_dto(evidence)

    def get_by_product(self, product_id: str) -> List[EvidenceDTO]:
        evidences = self.service.repository.find_by_product(product_id)
        return [self._to_evidence_dto(e) for e in evidences]

    def verify_evidence(self, evidence_id: str, verdict: str) -> EvidenceDTO:
        evidence = self.service.verify_evidence(evidence_id, verdict)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return self._to_evidence_dto(evidence)

    def detect_conflicts(self, product_id: str) -> List[ConflictEntryDTO]:
        conflicts = self.service.detect_conflicts(product_id)
        return [self._to_conflict_dto(c) for c in conflicts]

    def resolve_conflict(self, evidence_id: str, resolution: str) -> EvidenceDTO:
        evidence = self.service.resolve_conflict(evidence_id, resolution)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return self._to_evidence_dto(evidence)

    def _to_evidence_dto(self, evidence) -> EvidenceDTO:
        return EvidenceDTO(
            evidence_id=evidence.evidence_id,
            product_id=evidence.product_id,
            claim_id=evidence.claim_id,
            field=evidence.field,
            claim=evidence.claim,
            claim_type=evidence.claim_type,
            source_type=evidence.source_type,
            source_reference=evidence.source_reference,
            source_date=evidence.source_date,
            evidence_date=evidence.evidence_date,
            evidence_strength=evidence.evidence_strength,
            evidence_status=evidence.evidence_status,
            conflict_status=evidence.conflict_status,
            market_region=evidence.market_region,
            notes=evidence.notes,
            qa_status=evidence.qa_status,
            created_at=evidence.created_at
        )

    def _to_conflict_dto(self, conflict: Dict) -> ConflictEntryDTO:
        return ConflictEntryDTO(
            field=conflict.get("field"),
            values=conflict.get("values", []),
            evidence_ids=conflict.get("evidence_ids", []),
            severity="HIGH",
            status="UNRESOLVED"
        )


class ProductKnowledgeFacade:
    def __init__(self, db: Session):
        self.db = db
        self.service = ProductKnowledgeService(db)

    def get_by_product(self, product_id: str) -> ProductKnowledgeDTO:
        knowledge = self.service.get_or_create(product_id)
        return self._to_knowledge_dto(knowledge)

    def refresh_from_evidence(self, product_id: str) -> ProductKnowledgeDTO:
        knowledge = self.service.update_from_evidence(product_id)
        return self._to_knowledge_dto(knowledge)

    def _to_knowledge_dto(self, knowledge) -> ProductKnowledgeDTO:
        return ProductKnowledgeDTO(
            product_knowledge_id=knowledge.product_knowledge_id,
            product_id=knowledge.product_id,
            ingredients=knowledge.ingredients,
            ingredient_roles=knowledge.ingredient_roles,
            claimed_benefits=knowledge.claimed_benefits,
            known_use_cases=knowledge.known_use_cases,
            contraindications=knowledge.contraindications,
            usage_instructions=knowledge.usage_instructions,
            manufacturer_claims=knowledge.manufacturer_claims,
            evidence_refs=knowledge.evidence_refs,
            evidence_status=knowledge.evidence_status,
            knowledge_confidence=knowledge.knowledge_confidence,
            created_at=knowledge.created_at,
            updated_at=knowledge.updated_at
        )

