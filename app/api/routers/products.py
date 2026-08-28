from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.interface.facades import ProductFacade
from app.interface.schemas import ProductCreate
from app.services.product_service import ProductService

router = APIRouter()


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.get("/")
async def list_products(db: Session = Depends(get_db)):
    facade = ProductFacade(db)
    return [_to_dict(p) for p in facade.get_verified_products()]


@router.get("/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    facade = ProductFacade(db)
    product = facade.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return _to_dict(product)


@router.get("/brand/{brand}")
async def get_products_by_brand(brand: str, db: Session = Depends(get_db)):
    facade = ProductFacade(db)
    return [_to_dict(p) for p in facade.find_by_brand(brand)]


@router.post("/", status_code=201)
async def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.create(**payload.model_dump())
    return _to_dict(product)
