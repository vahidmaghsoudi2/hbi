"""Read-only Product Acceptance Report API."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.authorization import require_any_role
from app.core.deps import get_db
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA
from app.services.acceptance_report_service import build_acceptance_reports

router = APIRouter()


class CohortAcceptanceReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_ids: List[str] = Field(min_length=1, max_length=500)
    cohort_label: Optional[str] = Field(default=None, max_length=120)
    include_evidence_details: bool = True


def _validate_product_ids(product_ids: List[str]) -> None:
    if any(not item or not item.strip() or len(item) > 128 for item in product_ids):
        raise HTTPException(
            status_code=422,
            detail="product_ids must contain non-empty strings of at most 128 characters",
        )
    if len(set(product_ids)) != len(product_ids):
        raise HTTPException(status_code=422, detail="product_ids must be unique")


@router.get("/api/v1/products/{product_id}/acceptance-report")
async def get_product_acceptance_report(
    product_id: str,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    reports, _audit_tables, errors = build_acceptance_reports(db, [product_id])
    if product_id not in reports:
        if product_id in errors:
            raise HTTPException(status_code=503, detail="Acceptance report source unavailable")
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return reports[product_id]


@router.post("/api/v1/acceptance-reports/cohort")
async def get_cohort_acceptance_report(
    request: CohortAcceptanceReportRequest,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    _validate_product_ids(request.product_ids)
    reports, _audit_tables, errors = build_acceptance_reports(db, request.product_ids)

    missing_ids = [
        product_id for product_id in request.product_ids
        if product_id not in reports and product_id not in errors
    ]
    failed_products = [
        {
            "product_id": product_id,
            "error_code": "REPORT_BUILD_FAILED",
            "message": "The report could not be built for this product.",
        }
        for product_id in request.product_ids
        if product_id in errors
    ]
    readiness_counts = {
        "ready": 0, "partial": 0, "blocked": 0, "not_assessed": 0,
    }
    for report in reports.values():
        status = report.get("evidence_readiness", "NOT_ASSESSED").lower()
        key = status if status in readiness_counts else "not_assessed"
        readiness_counts[key] += 1

    found = len(reports) + len(errors)
    successfully_reported = len(reports)
    failed = len(errors)
    report_status = (
        "FAILED" if request.product_ids and successfully_reported == 0 and failed > 0
        else "COMPLETED_WITH_ERRORS" if missing_ids or failed
        else "COMPLETED"
    )
    if not request.include_evidence_details:
        for report in reports.values():
            report["evidence"] = []

    return {
        "schema_version": "1.0.0",
        "cohort_label": request.cohort_label,
        "report_status": report_status,
        "requested": len(request.product_ids),
        "found": found,
        "missing": len(missing_ids),
        "successfully_reported": successfully_reported,
        "failed": failed,
        **readiness_counts,
        "missing_product_ids": missing_ids,
        "failed_products": failed_products,
        "reports": [reports[product_id] for product_id in request.product_ids if product_id in reports],
    }
