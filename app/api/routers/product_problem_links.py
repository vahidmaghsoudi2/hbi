from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.authorization import require_any_role
from app.core.deps import get_db
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.interface.product_problem_link_schemas import (
    ProductProblemLinkCreate,
    ProductProblemLinkReassess,
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


@router.post("/", response_model=ProductProblemLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_product_problem_link(
    payload: ProductProblemLinkCreate,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    data = payload.model_dump()
    reason = data.pop("reason")
    try:
        record = ProductProblemLinkService(db).create_link(
            **data, reason=reason, actor_id=subject_id, actor_role=sorted(roles)[0]
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
            extra={"actor_role": sorted(roles)},
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


@router.post("/{link_id}/reassess", response_model=ProductProblemLinkResponse, status_code=status.HTTP_201_CREATED)
async def reassess_product_problem_link(
    link_id: str,
    payload: ProductProblemLinkReassess,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    data = payload.model_dump()
    expected_revision_no = data.pop("expected_revision_no")
    reason = data.pop("reason")
    try:
        record = ProductProblemLinkService(db).reassess_link(
            link_id, expected_revision_no=expected_revision_no,
            **data, reason=reason, actor_id=subject_id, actor_role=sorted(roles)[0]
        )
        db.commit()
    except (NotFoundError, ValidationError, ConflictError) as exc:
        db.rollback()
        audit_event(
            "product_problem_link_reassess",
            customer_id=subject_id,
            path=f"/api/v1/product-problem-links/{link_id}/reassess",
            outcome="denied",
            detail=str(exc),
            extra={"actor_role": sorted(roles), "link_id": link_id},
        )
        _raise_http_domain_error(exc)

    audit_event(
        "product_problem_link_reassess",
        customer_id=subject_id,
        path=f"/api/v1/product-problem-links/{link_id}/reassess",
        outcome="ok",
        detail=record.link_id,
        extra={
            "actor_role": sorted(roles),
            "product_id": record.product_id,
            "problem_id": record.problem_id,
            "relationship_status": record.relationship_status,
            "supersedes_link_id": record.supersedes_link_id,
            "revision_no": record.revision_no,
        },
    )
    return ProductProblemLinkResponse.model_validate(record)


@router.get("/{link_id}/history")
async def get_product_problem_link_history(
    link_id: str,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        result = ProductProblemLinkService(db).history(link_id)
    except (NotFoundError, ValidationError, ConflictError) as exc:
        _raise_http_domain_error(exc)
    return {
        "assessments": [ProductProblemLinkResponse.model_validate(row).model_dump(mode="json") for row in result["assessments"]],
        "events": [
            {
                "event_id": row.event_id, "link_id": row.link_id,
                "revision_no": row.revision_no, "actor_id": row.actor_id,
                "actor_role": row.actor_role, "event_type": row.event_type,
                "reason": row.reason, "before_state": row.before_state,
                "after_state": row.after_state, "correlation_id": row.correlation_id,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            } for row in result["events"]
        ],
    }


@router.get("/", response_model=List[ProductProblemLinkResponse])
async def list_product_problem_links(
    product_id: Optional[str] = Query(default=None, min_length=1, max_length=128),
    problem_id: Optional[str] = Query(default=None, min_length=3, max_length=3, pattern=r"^P\d{2}$"),
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    if bool(product_id) == bool(problem_id):
        raise HTTPException(status_code=422, detail="Provide exactly one of product_id or problem_id.")
    service = ProductProblemLinkService(db)
    try:
        records = service.list_by_product(product_id) if product_id is not None else service.list_by_problem(problem_id)
    except (NotFoundError, ValidationError, ConflictError) as exc:
        _raise_http_domain_error(exc)
    return [ProductProblemLinkResponse.model_validate(row) for row in records]
