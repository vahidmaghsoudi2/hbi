"""Product duplicate/naming review API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.authorization import require_any_role
from app.core.exceptions import ValidationError
from app.interface.schemas import DuplicateCheckRequest, DuplicateCheckOperatorDecision
from app.models.user_role import ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN
from app.services.duplicate_check_service import DuplicateCheckService

router = APIRouter()


@router.post("/", status_code=200)
async def check_duplicate(
    payload: DuplicateCheckRequest,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    return DuplicateCheckService(db).check(payload.model_dump(exclude_unset=True), actor_id=subject_id, roles=roles)


@router.post("/audit/{check_id}/decision")
async def record_operator_decision(
    check_id: str,
    payload: DuplicateCheckOperatorDecision,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    return DuplicateCheckService(db).record_operator_decision(
        check_id=check_id,
        decision=payload.decision,
        selected_product_id=payload.selected_product_id,
        final_product_name=payload.final_product_name,
        reason=payload.reason,
        actor_id=subject_id,
        roles=roles,
    )


@router.get("/audit")
async def list_duplicate_audits(
    product_id: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    rows = DuplicateCheckService(db).list_audits(product_id=product_id, limit=limit)
    return [
        {
            "check_id": row.check_id,
            "timestamp": row.timestamp,
            "actor_id": row.actor_id,
            "actor_role": row.actor_role,
            "result": row.result,
            "product_id": row.product_id,
            "input_snapshot": row.input_snapshot,
            "candidates": row.candidates,
            "operator_decision": row.operator_decision,
        }
        for row in rows
    ]
