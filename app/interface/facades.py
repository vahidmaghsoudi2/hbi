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

def _to_recommendation_dto(r) -> RecommendationDTO:
    return RecommendationDTO(
        recommendation_id=r.recommendation_id,
        case_id=r.case_id,
        product_id=r.product_id,
        need_match_score=r.need_match_score,
        eligibility_status=r.eligibility_status,
        ranking_score=r.ranking_score,
        ranking_reasons=r.ranking_reasons
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
        self.service = RecommendationService(db)

    def generate(self, case_id: str, customer_profile: Dict) -> List[RecommendationDTO]:
        recommendations = self.service.generate_recommendations(case_id, customer_profile)
        return [_to_recommendation_dto(r) for r in recommendations]

    def find_by_case(self, case_id: str) -> List[RecommendationDTO]:
        recommendations = self.service.find_by_case(case_id)
        return [_to_recommendation_dto(r) for r in recommendations]

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
