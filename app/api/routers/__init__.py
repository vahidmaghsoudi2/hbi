from app.api.routers.auth import router as auth_router
from app.api.routers.products import router as products_router
from app.api.routers.customers import router as customers_router
from app.api.routers.cases import router as cases_router
from app.api.routers.recommendations import router as recommendations_router
from app.api.routers.inventory import router as inventory_router
from app.api.routers.sales import router as sales_router
from app.api.routers.evidence import router as evidence_router
from app.api.routers.payments import router as payments_router

__all__ = [
    "auth_router", "products_router", "customers_router", "cases_router",
    "recommendations_router", "inventory_router", "sales_router", "evidence_router",
    "payments_router",
]
