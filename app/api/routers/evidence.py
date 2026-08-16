from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.interface.schemas import (
    EvidenceCreate, EvidenceUpdate, EvidenceResponse,
    VerifyRequest, ResolveConflictRequest,
    ProductKnowledgeResponse, ConflictEntryResponse
)
from app.interface.facades import EvidenceFacade, ProductKnowledgeFacade

router = APIRouter()


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    data: EvidenceCreate,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = EvidenceFacade(db)
    try:
        evidence_dto = facade.add_evidence(data.model_dump())
        return EvidenceResponse.model_validate(evidence_dto.__dict__)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/conflicts/{product_id}", response_model=List[ConflictEntryResponse])
async def detect_conflicts(
    product_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = EvidenceFacade(db)
    conflicts = facade.detect_conflicts(product_id)
    return [ConflictEntryResponse.model_validate(c.__dict__) for c in conflicts]


@router.get("/knowledge/{product_id}", response_model=ProductKnowledgeResponse)
async def get_product_knowledge(
    product_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = ProductKnowledgeFacade(db)
    dto = facade.get_by_product(product_id)
    return ProductKnowledgeResponse.model_validate(dto.__dict__)


@router.post("/knowledge/{product_id}/refresh", response_model=ProductKnowledgeResponse)
async def refresh_product_knowledge(
    product_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = ProductKnowledgeFacade(db)
    dto = facade.refresh_from_evidence(product_id)
    return ProductKnowledgeResponse.model_validate(dto.__dict__)


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    product_id: Optional[str] = None,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = EvidenceFacade(db)
    if product_id:
        dtos = facade.get_by_product(product_id)
    else:
        service = facade.service
        evidences = service.get_all()
        dtos = [facade._to_evidence_dto(e) for e in evidences]
    return [EvidenceResponse.model_validate(dto.__dict__) for dto in dtos]


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    service = EvidenceFacade(db).service
    evidence = service.get_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail=f"Evidence {evidence_id} not found")
    dto = EvidenceFacade(db)._to_evidence_dto(evidence)
    return EvidenceResponse.model_validate(dto.__dict__)


@router.post("/{evidence_id}/verify", response_model=EvidenceResponse)
async def verify_evidence(
    evidence_id: str,
    request: VerifyRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = EvidenceFacade(db)
    try:
        dto = facade.verify_evidence(evidence_id, request.verdict)
        return EvidenceResponse.model_validate(dto.__dict__)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{evidence_id}/resolve", response_model=EvidenceResponse)
async def resolve_conflict(
    evidence_id: str,
    request: ResolveConflictRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = EvidenceFacade(db)
    try:
        dto = facade.resolve_conflict(evidence_id, request.resolution)
        return EvidenceResponse.model_validate(dto.__dict__)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
