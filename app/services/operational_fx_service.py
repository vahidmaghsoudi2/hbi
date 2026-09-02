"""Operational FX rate service.

OperationalFxRate is the *current* rate for new operations that choose to
read it. It must NEVER cascade-update historical Sale / Payment /
StockMovement / SaleReturn / SaleItem money snapshots.
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.operational_fx_rate import OperationalFxRate
from app.services.currency_fx import validate_fx_rate


class OperationalFxService:
    def __init__(self, db: Session):
        self.db = db

    def get_current(self) -> Optional[OperationalFxRate]:
        return (
            self.db.query(OperationalFxRate)
            .order_by(
                OperationalFxRate.effective_at.desc(),
                OperationalFxRate.created_at.desc(),
                OperationalFxRate.rate_id.desc(),
            )
            .first()
        )

    def get_current_rate(self) -> Optional[float]:
        row = self.get_current()
        return float(row.fx_rate_usd_to_irr) if row else None

    def set_rate(
        self,
        fx_rate_usd_to_irr: float,
        *,
        note: Optional[str] = None,
    ) -> OperationalFxRate:
        rate = validate_fx_rate(fx_rate_usd_to_irr)
        try:
            row = OperationalFxRate(
                rate_id=str(uuid.uuid4()),
                fx_rate_usd_to_irr=rate,
                note=note,
            )
            self.db.add(row)
            self.db.flush()
            return row
        except Exception:
            self.db.rollback()
            raise
