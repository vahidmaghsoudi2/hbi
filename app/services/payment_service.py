"""Phase 09 — Payment workflow on existing Payment + Sale entities.

Methods allowed by schema: CASH, CARD, TRANSFER, OTHER.
No payment-status state machine (schema has no status field).
Does not modify Sale monetary totals (historical sale values preserved).
C-01: amount_irr = amount_usd * R; amount_toman = amount_irr / 10.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.sale import Sale
from app.services.stock_in_service import irr_to_toman, usd_to_irr

VALID_METHODS = frozenset({"CASH", "CARD", "TRANSFER", "OTHER"})


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def list_by_sale(self, sale_id: str) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.sale_id == sale_id)
            .order_by(Payment.created_at.asc(), Payment.payment_id.asc())
            .all()
        )

    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.payment_id == payment_id)
            .first()
        )

    def record_payment(
        self,
        *,
        sale_id: str,
        method: str,
        amount_usd: float,
        fx_rate_usd_to_irr: float,
        note: Optional[str] = None,
    ) -> Payment:
        if not sale_id:
            raise ValueError("sale_id is required")
        method_u = (method or "").strip().upper()
        if method_u not in VALID_METHODS:
            raise ValueError(
                f"invalid payment method: {method}; allowed={sorted(VALID_METHODS)}"
            )
        if amount_usd is None or float(amount_usd) <= 0:
            raise ValueError("amount_usd must be > 0")
        amount_usd = float(amount_usd)
        if fx_rate_usd_to_irr is None or float(fx_rate_usd_to_irr) <= 0:
            raise ValueError(
                "fx_rate_usd_to_irr must be > 0 (caller-supplied; never invented)"
            )
        fx_rate = float(fx_rate_usd_to_irr)

        sale = self.db.query(Sale).filter(Sale.sale_id == sale_id).first()
        if not sale:
            raise ValueError(f"Sale {sale_id} not found")

        # Capture sale totals before payment (must remain unchanged)
        prior_usd = sale.total_amount_usd
        prior_irr = sale.total_amount_irr
        prior_toman = sale.total_amount_toman
        prior_fx = sale.fx_rate_usd_to_irr

        amount_irr = usd_to_irr(amount_usd, fx_rate)
        amount_toman = irr_to_toman(amount_irr)

        try:
            payment = Payment(
                payment_id=str(uuid.uuid4()),
                sale_id=sale_id,
                method=method_u,
                amount_usd=amount_usd,
                fx_rate_usd_to_irr=fx_rate,
                amount_irr=amount_irr,
                amount_toman=int(round(amount_toman)),
                note=note,
            )
            self.db.add(payment)
            self.db.flush()

            # Ensure sale historical values not mutated
            self.db.refresh(sale)
            if sale.total_amount_usd != prior_usd:
                raise RuntimeError("sale total_amount_usd corrupted by payment")
            if sale.total_amount_irr != prior_irr:
                raise RuntimeError("sale total_amount_irr corrupted by payment")
            if sale.total_amount_toman != prior_toman:
                raise RuntimeError("sale total_amount_toman corrupted by payment")
            if sale.fx_rate_usd_to_irr != prior_fx:
                raise RuntimeError("sale fx_rate corrupted by payment")

            return payment
        except Exception:
            self.db.rollback()
            raise
