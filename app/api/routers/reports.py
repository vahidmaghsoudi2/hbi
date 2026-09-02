from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.services.report_service import ReportService, DEFAULT_LOW_STOCK

router = APIRouter()


@router.get("/sales/period/{kind}")
async def sales_period_report(
    kind: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    if kind not in ("today", "week", "month"):
        raise HTTPException(status_code=422, detail="kind must be today|week|month")
    try:
        return ReportService(db).sales_period(kind)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/sales/range")
async def sales_range_report(
    start: datetime = Query(...),
    end: datetime = Query(...),
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    try:
        return ReportService(db).sales_report(start=start, end=end)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/inventory")
async def inventory_all_report(
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    return ReportService(db).inventory_all()


@router.get("/inventory/category/{category_id}")
async def inventory_by_category_report(
    category_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    try:
        return ReportService(db).inventory_by_category(category_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/inventory/low-stock")
async def inventory_low_stock_report(
    threshold: int = Query(DEFAULT_LOW_STOCK, ge=0),
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    try:
        return ReportService(db).inventory_low_stock(threshold)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/financial")
async def financial_summary_report(
    start: datetime = Query(...),
    end: datetime = Query(...),
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    try:
        return ReportService(db).financial_summary(start=start, end=end)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/categories")
async def categories_report(
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    return ReportService(db).categories_locked()
