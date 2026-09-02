"""Phase 06 — Stock Movement Ledger service (read/trace only)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement
from app.repositories.stock_movement_repository import (
    VALID_MOVEMENT_TYPES,
    StockMovementRepository,
)


class StockMovementService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = StockMovementRepository(db)

    def get_by_id(self, movement_id: str) -> Optional[StockMovement]:
        return self.repository.get_by_id(movement_id)

    def list_ledger(
        self,
        *,
        product_id: Optional[str] = None,
        movement_type: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StockMovement]:
        if movement_type is not None and movement_type not in VALID_MOVEMENT_TYPES:
            raise ValueError(
                f"invalid movement_type: {movement_type}; "
                f"allowed={sorted(VALID_MOVEMENT_TYPES)}"
            )
        return self.repository.list_ledger(
            product_id=product_id,
            movement_type=movement_type,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )
