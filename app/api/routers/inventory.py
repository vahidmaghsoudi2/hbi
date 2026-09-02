from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import InventoryFacade
from app.interface.errors import NotFoundError
from app.services.inventory_service import InventoryService

router = APIRouter()


def _to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


class StockAdjustRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    direction: str = Field(..., description="increase | decrease")
    note: Optional[str] = None


@router.get("/")
async def list_inventory(db: Session = Depends(get_db)):
    facade = InventoryFacade(db)
    return [_to_dict(i) for i in facade.list_all()]


@router.get("/available")
async def get_available_inventory(db: Session = Depends(get_db)):
    facade = InventoryFacade(db)
    return [_to_dict(i) for i in facade.find_available()]


@router.get("/product/{product_id}")
async def get_inventory_by_product(product_id: str, db: Session = Depends(get_db)):
    facade = InventoryFacade(db)
    try:
        inv = facade.get_by_product(product_id)
        return _to_dict(inv)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/availability/{product_id}")
async def get_availability(product_id: str, db: Session = Depends(get_db)):
    svc = InventoryService(db)
    sellable = svc.sellable_quantity(product_id)
    available = svc.is_available(product_id, 1)
    return {
        "product_id": product_id,
        "available": available,
        "sellable_quantity": sellable,
        "status": "AVAILABLE" if available else "OUT_OF_STOCK",
    }


@router.post("/adjust")
async def adjust_stock(
    body: StockAdjustRequest,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    """Authorized inventory increase/decrease with StockMovement trace."""
    svc = InventoryService(db)
    direction = body.direction.strip().lower()
    try:
        if direction == "increase":
            inv = svc.increase_stock(body.product_id, body.quantity, note=body.note)
        elif direction == "decrease":
            inv = svc.decrease_stock(body.product_id, body.quantity, note=body.note)
        else:
            raise HTTPException(status_code=422, detail="direction must be increase or decrease")
        db.commit()
        db.refresh(inv)
        return _to_dict(inv)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
