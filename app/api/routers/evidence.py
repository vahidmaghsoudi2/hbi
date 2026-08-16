from fastapi import APIRouter, HTTPException, status

router = APIRouter()

_MSG = "Evidence endpoints temporarily disabled. EvidenceService and EvidenceRepository do not exist. Awaiting Phase 3."


@router.get("/")
async def list_evidence():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_MSG)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_evidence():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_MSG)


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_MSG)
