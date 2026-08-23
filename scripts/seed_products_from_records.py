"""Seed Product + Inventory (+ minimal ProductKnowledge from category only) from data/seed_products.json.

NO invented evidence. Source of truth: docs/01_product_records.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db, engine
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.product_knowledge import ProductKnowledge

ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "seed_products.json"


def load_seed() -> dict:
    with open(SEED_PATH, encoding="utf-8") as f:
        return json.load(f)


def seed(db: Session) -> int:
    data = load_seed()
    n = 0
    for p in data["products"]:
        existing = db.get(Product, p["product_id"])
        if existing is None:
            db.add(
                Product(
                    product_id=p["product_id"],
                    brand=p["brand"],
                    product_name=p["product_name"],
                    variant=p.get("variant"),
                    size_value=p.get("size_value"),
                    size_unit=p.get("size_unit"),
                    barcode_gtin=p.get("barcode_gtin"),
                    market_region=p.get("market_region"),
                    packaging_version=p.get("packaging_version"),
                    identity_status=p["identity_status"],
                    qa_verdict=p.get("qa_verdict", "PENDING"),
                )
            )
        inv_id = f"INV-{p['product_id']}"
        inv = db.get(Inventory, inv_id)
        qty = int(p.get("inventory_count") or 0)
        if inv is None:
            db.add(
                Inventory(
                    inventory_id=inv_id,
                    product_id=p["product_id"],
                    quantity_available=qty,
                    quantity_reserved=0,
                    quantity_damaged=0,
                    stock_status="AVAILABLE" if qty > 0 else "OUT_OF_STOCK",
                )
            )
        # ProductKnowledge: only category as known_use_cases — not clinical claims
        pk_id = f"PK-{p['product_id']}"
        pk = db.get(ProductKnowledge, pk_id)
        category = (p.get("category") or "").strip()
        if pk is None and category:
            db.add(
                ProductKnowledge(
                    product_knowledge_id=pk_id,
                    product_id=p["product_id"],
                    known_use_cases=category,
                    claimed_benefits=None,
                    ingredients=None,
                )
            )
        n += 1
    db.commit()
    return n


def main() -> None:
    os.makedirs(ROOT / "data", exist_ok=True)
    init_db()
    db = SessionLocal()
    try:
        count = seed(db)
        print(f"SEED_OK products={count} path={SEED_PATH}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
