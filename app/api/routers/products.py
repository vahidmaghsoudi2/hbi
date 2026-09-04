"""P4 P0 — Product API with AuthN/AuthZ, informational PATCH, controlled transitions."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.authorization import get_current_subject_and_roles, require_any_role
from app.core.exceptions import NotFoundError, ValidationError
from app.core.governance import can_view_mutation_log
from app.interface.facades import ProductFacade
from app.interface.schemas import (
    ProductCreate, ProductUpdate, ProductTransitionRequest, ProductRejectRequest,
    ProductQARequest, ProductIdentityVerifyRequest,
)
from app.services.product_service import ProductService
from app.services.product_transition_service import ProductTransitionService
from app.services.mutation_log_service import MutationLogService
from app.models.user_role import ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA, ROLE_ADMIN

router = APIRouter()


def _to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


def _http_from_domain(exc):
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=422, detail=str(exc))
    raise exc


@router.get("/")
async def list_products(db: Session = Depends(get_db)):
    return [_to_dict(p) for p in ProductFacade(db).get_verified_products()]


@router.get("/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = ProductFacade(db).get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return _to_dict(product)


@router.get("/brand/{brand}")
async def get_products_by_brand(brand: str, db: Session = Depends(get_db)):
    return [_to_dict(p) for p in ProductFacade(db).find_by_brand(brand)]


@router.post("/", status_code=201)
async def create_product(
    payload: ProductCreate, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    try:
        product = ProductService(db).create_product_with_inventory(
            payload.model_dump(exclude_unset=True), actor_id=subject_id, roles=roles)
        return _to_dict(product)
    except Exception as e:
        _http_from_domain(e)


@router.patch("/{product_id}")
async def update_product(
    product_id: str, payload: ProductUpdate, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    subject_id, roles = auth
    try:
        return _to_dict(ProductService(db).edit_informational(
            product_id, payload.model_dump(exclude_unset=True), actor_id=subject_id, roles=roles))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/submit")
async def submit_product(product_id: str, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).submit(product_id, subject_id, roles))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/enter-qa-review")
async def enter_qa_review(product_id: str, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).enter_qa_review(product_id, subject_id, roles))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/approve")
async def approve_product(product_id: str, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).approve(product_id, subject_id, roles))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/reject")
async def reject_product(product_id: str, body: ProductRejectRequest, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).reject(product_id, subject_id, roles, body.reason))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/activate")
async def activate_product(product_id: str, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).activate(product_id, subject_id, roles))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/archive")
async def archive_product(product_id: str, body: ProductTransitionRequest = None,
    db: Session = Depends(get_db), auth=Depends(require_any_role(ROLE_PO))):
    subject_id, roles = auth
    reason = body.reason if body else None
    try:
        return _to_dict(ProductTransitionService(db).archive(product_id, subject_id, roles, reason=reason))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/qa")
async def product_qa_decision(product_id: str, body: ProductQARequest, db: Session = Depends(get_db),
    auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).set_product_qa(
            product_id, subject_id, roles, body.verdict, notes=body.notes))
    except Exception as e:
        _http_from_domain(e)


@router.post("/{product_id}/verify-identity")
async def verify_identity(product_id: str, body: ProductIdentityVerifyRequest,
    db: Session = Depends(get_db), auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO))):
    subject_id, roles = auth
    try:
        return _to_dict(ProductTransitionService(db).verify_identity(
            product_id, subject_id, roles, body.identity_status,
            source_refs=body.source_refs, confidence=body.confidence))
    except Exception as e:
        _http_from_domain(e)


@router.get("/{product_id}/mutation-log")
async def get_mutation_log(product_id: str, db: Session = Depends(get_db),
    auth=Depends(get_current_subject_and_roles)):
    subject_id, roles = auth
    if not can_view_mutation_log(roles):
        raise HTTPException(status_code=403, detail="Not authorized to view mutation log")
    return [_to_dict(r) for r in MutationLogService(db).list_for_product(product_id)]
