from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.authorization import require_any_role
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR
from app.interface.facades import InventoryFacade
from app.interface.errors import NotFoundError
from app.services.inventory_service import InventoryService
from app.services.stock_movement_service import StockMovementService
from app.services.stock_in_service import StockInService
from app.services.operational_fx_service import OperationalFxService
from app.services.currency_fx import usd_to_irr, irr_to_toman

router = APIRouter()

_require_inventory_admin = require_any_role(ROLE_ADMIN)
_require_inventory_sell_read = require_any_role(ROLE_ADMIN, ROLE_EDITOR)


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


class StockInRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    purchase_price_usd: float = Field(..., ge=0)
    fx_rate_usd_to_irr: float = Field(..., gt=0, description="IRR per 1 USD; required, never invented")
    note: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


@router.get("/")
async def list_inventory(
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    facade = InventoryFacade(db)
    return [_to_dict(i) for i in facade.list_all()]


@router.get("/available")
async def get_available_inventory(
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    facade = InventoryFacade(db)
    return [_to_dict(i) for i in facade.find_available()]


@router.get("/movements")
async def list_stock_movements(
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
    product_id: Optional[str] = Query(None),
    movement_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    svc = StockMovementService(db)
    try:
        rows = svc.list_ledger(product_id=product_id, movement_type=movement_type, limit=limit, offset=offset)
        return [_to_dict(r) for r in rows]
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/movements/{movement_id}")
async def get_stock_movement(
    movement_id: str,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    svc = StockMovementService(db)
    row = svc.get_by_id(movement_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"StockMovement {movement_id} not found")
    return _to_dict(row)


class SalePriceSetRequest(BaseModel):
    sale_price_usd: float = Field(..., ge=0)


@router.put("/product/{product_id}/sale-price")
async def set_sale_price(
    product_id: str,
    body: SalePriceSetRequest,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    svc = InventoryService(db)
    try:
        inv = svc.set_sale_price_usd(product_id, body.sale_price_usd)
        db.commit()
        db.refresh(inv)
        return _to_dict(inv)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/product/{product_id}")
async def get_inventory_by_product(
    product_id: str,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_sell_read),
):
    facade = InventoryFacade(db)
    try:
        inv = facade.get_by_product(product_id)
        data = _to_dict(inv)
        fx = OperationalFxService(db).get_current_rate()
        usd = inv.sale_price_usd
        data["current_fx_rate_usd_to_irr"] = fx
        data["current_sale_price_irr"] = usd_to_irr(usd, fx) if usd is not None and fx is not None else None
        data["current_sale_price_toman"] = (
            int(round(irr_to_toman(data["current_sale_price_irr"])))
            if data["current_sale_price_irr"] is not None else None
        )
        return data
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/availability/{product_id}")
async def get_availability(
    product_id: str,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    svc = InventoryService(db)
    sellable = svc.sellable_quantity(product_id)
    available = svc.is_available(product_id, 1)
    return {"product_id": product_id, "available": available, "sellable_quantity": sellable,
            "status": "AVAILABLE" if available else "OUT_OF_STOCK"}


@router.post("/stock-in")
async def stock_in(
    body: StockInRequest,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
    svc = StockInService(db)
    try:
        result = svc.stock_in(product_id=body.product_id, quantity=body.quantity,
                              purchase_price_usd=body.purchase_price_usd,
                              fx_rate_usd_to_irr=body.fx_rate_usd_to_irr, note=body.note,
                              reference_type=body.reference_type, reference_id=body.reference_id)
        db.commit()
        inv = result["inventory"]
        mov = result["movement"]
        db.refresh(inv)
        db.refresh(mov)
        return {"inventory": _to_dict(inv), "movement": _to_dict(mov), "before_quantity": result["before_quantity"]}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/adjust")
async def adjust_stock(
    body: StockAdjustRequest,
    db: Session = Depends(get_db),
    _authz: tuple = Depends(_require_inventory_admin),
):
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
