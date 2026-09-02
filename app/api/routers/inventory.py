from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import InventoryFacade
from app.interface.errors import NotFoundError
from app.services.inventory_service import InventoryService
from app.services.stock_movement_service import StockMovementService

router = APIRouter()


def _to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        data = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        for key, val in list(data.items()):
            if isinstance(val, datetime):
                data[key] = val.isoformat()
        return data
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


@router.get("/movements")
async def list_stock_movements(
    db: Session = Depends(get_db),
    product_id: Optional[str] = Query(None),
    movement_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Phase 06 — Stock movement ledger list with optional filters."""
    svc = StockMovementService(db)
    try:
        rows = svc.list_ledger(
            product_id=product_id,
            movement_type=movement_type,
            limit=limit,
            offset=offset,
        )
        return [_to_dict(r) for r in rows]
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/movements/{movement_id}")
async def get_stock_movement(movement_id: str, db: Session = Depends(get_db)):
    svc = StockMovementService(db)
    row = svc.get_by_id(movement_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"StockMovement {movement_id} not found")
    return _to_dict(row)


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
