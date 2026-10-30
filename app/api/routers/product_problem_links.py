from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.authorization import require_any_role
from app.core.deps import get_db
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.interface.product_problem_link_schemas import (
    ProductProblemLinkCreate,
    ProductProblemLinkResponse,
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA
from app.services.product_problem_link_service import ProductProblemLinkService

router = APIRouter()


def _raise_http_domain_error(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    raise exc


@router.post(
    "/",
    response_model=ProductProblemLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_problem_link(
    payload: ProductProblemLinkCreate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_PO, ROLE_ADMIN)),
):
    """Create an append-only assessment; only PO/Admin may write."""
    subject_id, roles = auth
    try:
        record = ProductProblemLinkService(db).create_link(
            **payload.model_dump()
        )
        db.commit()
    except (NotFoundError, ValidationError, ConflictError) as exc:
        db.rollback()
        audit_event(
            "product_problem_link_create",
            customer_id=subject_id,
            path="/api/v1/product-problem-links/",
            outcome="denied",
            detail=str(exc),
        )
        _raise_http_domain_error(exc)

    audit_event(
        "product_problem_link_create",
        customer_id=subject_id,
        path="/api/v1/product-problem-links/",
        outcome="ok",
        detail=record.link_id,
        extra={
            "actor_role": sorted(roles),
            "product_id": record.product_id,
            "problem_id": record.problem_id,
            "relationship_status": record.relationship_status,
        },
    )
    return ProductProblemLinkResponse.model_validate(record)


@router.get(
    "/",
    response_model=List[ProductProblemLinkResponse],
)
async def list_product_problem_links(
    product_id: Optional[str] = Query(default=None, min_length=1, max_length=128),
    problem_id: Optional[str] = Query(default=None, min_length=3, max_length=3, pattern=r"^P\d{2}$"),
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    """Read links by exactly one bounded selector; no unfiltered collection endpoint."""
    if bool(product_id) == bool(problem_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide exactly one of product_id or problem_id.",
        )

    service = ProductProblemLinkService(db)
    try:
        records = (
            service.list_by_product(product_id)
            if product_id is not None
            else service.list_by_problem(problem_id)
        )
    except (NotFoundError, ValidationError, ConflictError) as exc:
        _raise_http_domain_error(exc)

    return [ProductProblemLinkResponse.model_validate(row) for row in records]
