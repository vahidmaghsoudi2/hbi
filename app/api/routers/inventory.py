from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.interface.facades import InventoryFacade

router = APIRouter()


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.get("/product/{product_id}")
async def get_inventory_by_product(product_id: str, db: Session = Depends(get_db)):
    facade = InventoryFacade(db)
    inventory = facade.get_by_product(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail=f"Inventory for product {product_id} not found")
    return _to_dict(inventory)


@router.get("/available")
async def get_available_inventory(db: Session = Depends(get_db)):
    facade = InventoryFacade(db)
    return [_to_dict(i) for i in facade.find_available()]
