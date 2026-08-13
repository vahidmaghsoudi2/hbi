from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ProductDTO:
    product_id: str
    brand: str
    product_name: str
    identity_status: str
    qa_verdict: str
    variant: Optional[str] = None
    size_value: Optional[float] = None
    size_unit: Optional[str] = None

@dataclass
class CustomerDTO:
    customer_id: str
    name: str
    mobile: Optional[str] = None
    consent_to_store_data: int = 0

@dataclass
class CaseDTO:
    case_id: str
    customer_id: str
    case_type: str

@dataclass
class RecommendationDTO:
    recommendation_id: str
    case_id: str
    product_id: str
    need_match_score: Optional[float] = None
    eligibility_status: Optional[str] = None
    ranking_score: Optional[float] = None
    ranking_reasons: Optional[str] = None

@dataclass
class InventoryDTO:
    inventory_id: str
    product_id: str
    quantity_available: int
    quantity_reserved: int
    stock_status: str
    sale_price_toman: Optional[int] = None

@dataclass
class SaleItemDTO:
    sale_item_id: str
    sale_id: str
    product_id: str
    quantity: int
    unit_price_toman: int

@dataclass
class SaleDTO:
    sale_id: str
    customer_id: str
    total_amount_toman: int
    items: Optional[List[SaleItemDTO]] = None
