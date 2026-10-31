"""ProductKnowledge barriers: version scope, roles, other_attributes, domain conflict, NULL vs UNKNOWN."""
from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.services.product_knowledge_service import (
    ALLOWED_INGREDIENT_ROLES,
    ProductKnowledgeService,
    parse_role_entries,
)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(conn, _):
        conn.cursor().execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _seed_product(db, pid="P-BAR", *, market=None, packaging=None):
    db.add(
        Product(
            product_id=pid,
            brand="Brand",
            product_name="Item",
            market_region=market,
            packaging_version=packaging,
            identity_status="NEEDS_REVIEW",
            qa_verdict="PENDING",
            status="DRAFT",
            product_line="SKIN",
        )
    )
    db.flush()
    db.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=0,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="OUT_OF_STOCK",
        )
    )
    db.commit()


def _ev(db, *, pid, eid, field, claim, qa="VERIFIED", conflict="NONE", market=None, claim_type=None):
    db.add(
        Evidence(
            evidence_id=eid,
            product_id=pid,
            claim_id=f"CLM-{eid}",
            source_type="OFFICIAL_MANUFACTURER",
            source_reference="label",
            claim=claim,
            field=field,
            market_region=market,
            qa_status=qa,
            evidence_status="UNKNOWN",
            conflict_status=conflict,
            claim_type=claim_type,
        )
    )
    db.commit()


def test_parse_all_six_roles():
    for role in ALLOWED_INGREDIENT_ROLES:
        entries = parse_role_entries(f"Act:{role}")
        assert entries[0]["role"] == role


def test_version_isolation_does_not_merge_markets(db):
    _seed_product(db, pid="P-V", market="UK", packaging="v1")
    _ev(db, pid="P-V", eid="E-UK", field="ingredients", claim="Salicylic Acid", market="UK", qa="VERIFIED")
    _ev(db, pid="P-V", eid="E-US", field="ingredients", claim="Avobenzone", market="US", qa="VERIFIED")
    pk = ProductKnowledgeService(db).update_from_evidence("P-V")
    assert pk.ingredients is not None
    assert "Salicylic Acid" in pk.ingredients
    assert "Avobenzone" not in (pk.ingredients or "")
    domains = json.loads(pk.domain_evidence_status or "{}")
    assert domains.get("ingredients") in {"SUPPORTED", "PARTIAL", "CONFLICT", "UNKNOWN"}


def test_ingredient_roles_round_trip_all_six(db):
    _seed_product(db, pid="P-R")
    payload = [
        {"ingredient": "SA", "role": "CORE"},
        {"ingredient": "Glycerin", "role": "SUPPORT"},
        {"ingredient": "Fragrance", "role": "RISK"},
        {"ingredient": "Water", "role": "TECH"},
        {"ingredient": "Peptide", "role": "CLAIM-LINK"},
        {"ingredient": "Mystery", "role": "UNKNOWN"},
    ]
    _ev(
        db,
        pid="P-R",
        eid="E-ROLES",
        field="ingredient_roles",
        claim=json.dumps(payload),
        qa="VERIFIED",
    )
    pk = ProductKnowledgeService(db).update_from_evidence("P-R")
    roles = json.loads(pk.ingredient_roles)
    by_ing = {r["ingredient"]: r["role"] for r in roles}
    assert by_ing["SA"] == "CORE"
    assert by_ing["Fragrance"] == "RISK"
    assert by_ing["Mystery"] == "UNKNOWN"
    assert not (pk.contraindications and "Fragrance" in pk.contraindications)


def test_other_attributes_persist(db):
    _seed_product(db, pid="P-O")
    _ev(
        db,
        pid="P-O",
        eid="E-O",
        field="other_attributes",
        claim=json.dumps({"texture": "serum", "finish": "dewy"}),
        qa="VERIFIED",
    )
    pk = ProductKnowledgeService(db).update_from_evidence("P-O")
    attrs = json.loads(pk.other_attributes)
    assert attrs["texture"] == "serum"
    assert attrs["finish"] == "dewy"
    pk2 = ProductKnowledgeService(db).update_from_evidence("P-O")
    assert json.loads(pk2.other_attributes) == attrs


def test_partial_claim_conflict_does_not_wipe_supported_domain(db):
    _seed_product(db, pid="P-C")
    _ev(db, pid="P-C", eid="E1", field="known_use_cases", claim="spot-prone", qa="VERIFIED")
    _ev(
        db,
        pid="P-C",
        eid="E2",
        field="claimed_benefits",
        claim="cures acne",
        qa="VERIFIED",
        conflict="CONFLICT",
    )
    pk = ProductKnowledgeService(db).update_from_evidence("P-C")
    assert pk.known_use_cases and "spot-prone" in pk.known_use_cases
    domains = json.loads(pk.domain_evidence_status or "{}")
    assert domains.get("claimed_benefits") == "CONFLICT"
    assert domains.get("known_use_cases") == "SUPPORTED"
    assert pk.known_use_cases


def test_null_vs_unknown_evidence_status(db):
    _seed_product(db, pid="P-N")
    pk0 = ProductKnowledgeService(db).get_or_create("P-N")
    assert pk0.evidence_status is None

    pk1 = ProductKnowledgeService(db).update_from_evidence("P-N")
    assert pk1.evidence_status is None

    _ev(db, pid="P-N", eid="E-X", field="ingredients", claim="Water", qa="PENDING")
    pk2 = ProductKnowledgeService(db).update_from_evidence("P-N")
    assert pk2.evidence_status == "UNKNOWN"


def test_idempotent_rebuild(db):
    _seed_product(db, pid="P-I")
    _ev(db, pid="P-I", eid="E1", field="ingredients", claim="Niacinamide", qa="VERIFIED")
    s = ProductKnowledgeService(db)
    a = s.update_from_evidence("P-I")
    b = s.update_from_evidence("P-I")
    assert a.ingredients == b.ingredients
    assert a.evidence_status == b.evidence_status
    assert a.knowledge_confidence == b.knowledge_confidence


def test_rebuild_does_not_activate_product(db):
    _seed_product(db, pid="P-L")
    _ev(db, pid="P-L", eid="E1", field="ingredients", claim="Water", qa="VERIFIED")
    ProductKnowledgeService(db).update_from_evidence("P-L")
    p = db.query(Product).filter_by(product_id="P-L").one()
    assert p.status == "DRAFT"
    assert p.qa_verdict == "PENDING"
