"""Seed Product + Inventory + ProductKnowledge + Evidence from SoT JSON files.

Sources:
- data/seed_products.json ← docs/01_product_records
- data/seed_evidence.json ← docs/03_evidence_ledger (FACT/UNKNOWN only)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence

ROOT = Path(__file__).resolve().parents[1]
SEED_PRODUCTS = ROOT / "data" / "seed_products.json"
SEED_EVIDENCE = ROOT / "data" / "seed_evidence.json"


def _load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed_products(db: Session) -> int:
    data = _load(SEED_PRODUCTS)
    n = 0
    for p in data["products"]:
        if db.get(Product, p["product_id"]) is None:
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
                    status=p.get("status", "ACTIVE"),
                )
            )
        inv_id = f"INV-{p['product_id']}"
        if db.get(Inventory, inv_id) is None:
            qty = int(p.get("inventory_count") or 0)
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
        pk_id = f"PK-{p['product_id']}"
        category = (p.get("category") or "").strip()
        if db.get(ProductKnowledge, pk_id) is None and category:
            db.add(
                ProductKnowledge(
                    product_knowledge_id=pk_id,
                    product_id=p["product_id"],
                    known_use_cases=category,
                )
            )
        n += 1
    db.commit()
    return n


def seed_evidence(db: Session) -> int:
    if not SEED_EVIDENCE.exists():
        return 0
    data = _load(SEED_EVIDENCE)
    n = 0
    for e in data.get("evidence", data if isinstance(data, list) else []):
        eid = e.get("evidence_id")
        if not eid or db.get(Evidence, eid) is not None:
            continue
        db.add(
            Evidence(
                evidence_id=eid,
                product_id=e["product_id"],
                claim=e.get("claim", ""),
                source_type=e.get("source_type", "UNKNOWN"),
                source_reference=e.get("source_reference", ""),
                qa_status=e.get("qa_status", "PENDING"),
                conflict_status=e.get("conflict_status", "NONE"),
            )
        )
        n += 1
    db.commit()
    return n


def seed(db: Session | None = None) -> None:
    own = db is None
    if own:
        init_db()
        db = SessionLocal()
    try:
        seed_products(db)
        seed_evidence(db)
    finally:
        if own:
            db.close()


if __name__ == "__main__":
    seed()
