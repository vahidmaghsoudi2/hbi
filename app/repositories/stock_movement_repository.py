"""Phase 06 — StockMovement ledger repository (read + filter)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement
from app.repositories.base import BaseRepository

VALID_MOVEMENT_TYPES = frozenset(
    {"STOCK_IN", "PURCHASE", "SALE", "RETURN_IN", "RETURN_OUT", "ADJUSTMENT"}
)


class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, db: Session):
        super().__init__(StockMovement, db)

    def get_by_id(self, movement_id: str) -> Optional[StockMovement]:
        return (
            self.db.query(StockMovement)
            .filter(StockMovement.movement_id == movement_id)
            .first()
        )

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
        q = self.db.query(StockMovement)
        if product_id is not None:
            q = q.filter(StockMovement.product_id == product_id)
        if movement_type is not None:
            q = q.filter(StockMovement.movement_type == movement_type)
        if created_from is not None:
            q = q.filter(StockMovement.created_at >= created_from)
        if created_to is not None:
            q = q.filter(StockMovement.created_at <= created_to)
        return (
            q.order_by(StockMovement.created_at.desc(), StockMovement.movement_id.desc())
            .offset(max(0, offset))
            .limit(max(1, min(limit, 500)))
            .all()
        )

    def list_by_product(self, product_id: str, limit: int = 100) -> List[StockMovement]:
        return self.list_ledger(product_id=product_id, limit=limit)

    def list_by_type(self, movement_type: str, limit: int = 100) -> List[StockMovement]:
        return self.list_ledger(movement_type=movement_type, limit=limit)
