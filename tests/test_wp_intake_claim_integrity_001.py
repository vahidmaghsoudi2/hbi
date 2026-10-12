"""WP-INTAKE-CLAIM-INTEGRITY-001 — claim taxonomy and manufacturer-claim mapping."""
from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.exceptions import ValidationError
from app.domain.claim_taxonomy import ALLOWED_CLAIM_TYPES, normalize_claim_type_value
from app.interface.schemas import EvidenceCreate, EvidenceUpdate, ResearchAssertion
from app.models.base import Base
from app.models.evidence import Evidence
from app.models.product import Product
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService


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


def _product(db, product_id="P-CLAIM-001"):
    db.add(
        Product(
            product_id=product_id,
            brand="TestBrand",
            product_name="Claim Integrity Product",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.commit()


def test_allowed_claim_types_match_contract():
    assert ALLOWED_CLAIM_TYPES == {
        "FACT",
        "MANUFACTURER_CLAIM",
        "EVIDENCE",
        "INFERENCE",
        "UNKNOWN",
        "CONFLICT",
    }


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, "UNKNOWN"),
        ("", "UNKNOWN"),
        ("  fact ", "FACT"),
        ("manufacturer_claim", "MANUFACTURER_CLAIM"),
        ("INFERENCE", "INFERENCE"),
    ],
)
def test_normalize_claim_type_create_defaults(raw, expected):
    assert normalize_claim_type_value(raw, missing_default="UNKNOWN") == expected


def test_normalize_claim_type_update_none_means_omit():
    assert normalize_claim_type_value(None, missing_default=None) is None


def test_normalize_rejects_unsupported():
    with pytest.raises(ValueError, match="Unsupported claim_type"):
        normalize_claim_type_value("BENEFIT", missing_default="UNKNOWN")


def test_evidence_create_schema_rejects_benefit():
    with pytest.raises(PydanticValidationError):
        EvidenceCreate(
            product_id="P1",
            claim="x",
            source_type="MANUFACTURER",
            source_reference="ref",
            claim_type="BENEFIT",
        )


def test_evidence_create_schema_normalizes_case():
    body = EvidenceCreate(
        product_id="P1",
        claim="x",
        source_type="MANUFACTURER",
        source_reference="ref",
        claim_type="evidence",
    )
    assert body.claim_type == "EVIDENCE"


def test_evidence_update_schema_rejects_unsupported():
    with pytest.raises(PydanticValidationError):
        EvidenceUpdate(claim_type="BENEFIT")


def test_research_assertion_rejects_unsupported():
    with pytest.raises(PydanticValidationError):
        ResearchAssertion(
            claim="x",
            source_type="MANUFACTURER",
            source_reference="ref",
            claim_type="BENEFIT",
        )


def test_service_rejects_unsupported_claim_type_non_http(db):
    _product(db)
    svc = EvidenceService(db)
    with pytest.raises(ValidationError, match="Unsupported claim_type"):
        svc.add_evidence(
            {
                "product_id": "P-CLAIM-001",
                "claim": "bad type",
                "source_type": "MANUFACTURER",
                "source_reference": "test://legacy",
                "claim_type": "BENEFIT",
                "field": "claimed_benefits",
            },
            actor_id="tester",
            actor_role="Admin",
        )


def test_manufacturer_claim_field_requires_manufacturer_claim_type(db):
    """Named manufacturer_claim alias must not accept FACT into manufacturer_claims."""
    _product(db)
    db.add(
        Evidence(
            evidence_id="E-MFG-FACT",
            product_id="P-CLAIM-001",
            claim_id="C-MFG-FACT",
            field="manufacturer_claim",
            claim="fragrance-free",
            claim_type="FACT",
            source_type="PEER_REVIEWED",
            source_reference="test://fact",
            qa_status="VERIFIED",
            conflict_status="NONE",
            evidence_status="UNKNOWN",
        )
    )
    db.commit()
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-CLAIM-001")
    assert knowledge.manufacturer_claims is None


def test_manufacturer_claim_field_accepts_manufacturer_claim_type(db):
    _product(db)
    db.add(
        Evidence(
            evidence_id="E-MFG-OK",
            product_id="P-CLAIM-001",
            claim_id="C-MFG-OK",
            field="manufacturer_claim",
            claim="fragrance-free",
            claim_type="MANUFACTURER_CLAIM",
            source_type="MANUFACTURER",
            source_reference="test://mfg",
            qa_status="VERIFIED",
            conflict_status="NONE",
            evidence_status="UNKNOWN",
        )
    )
    db.commit()
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-CLAIM-001")
    assert knowledge.manufacturer_claims is not None
    assert "fragrance-free" in knowledge.manufacturer_claims


@pytest.mark.parametrize("claim_type", sorted(ALLOWED_CLAIM_TYPES - {"MANUFACTURER_CLAIM"}))
def test_manufacturer_claims_plural_rejects_non_manufacturer_types(db, claim_type):
    pid = f"P-{claim_type[:8]}"
    _product(db, product_id=pid)
    db.add(
        Evidence(
            evidence_id=f"E-{claim_type[:10]}",
            product_id=pid,
            claim_id=f"C-{claim_type[:10]}",
            field="manufacturer_claims",
            claim="only-mfg",
            claim_type=claim_type,
            source_type="MANUFACTURER" if claim_type != "FACT" else "PEER_REVIEWED",
            source_reference="test://plural",
            qa_status="VERIFIED",
            conflict_status="NONE",
            evidence_status="UNKNOWN",
        )
    )
    db.commit()
    knowledge = ProductKnowledgeService(db).update_from_evidence(pid)
    assert knowledge.manufacturer_claims is None


def test_conflict_excluded_from_manufacturer_claims(db):
    _product(db)
    db.add(
        Evidence(
            evidence_id="E-CONF",
            product_id="P-CLAIM-001",
            claim_id="C-CONF",
            field="manufacturer_claim",
            claim="should-not-appear",
            claim_type="MANUFACTURER_CLAIM",
            source_type="MANUFACTURER",
            source_reference="test://conflict",
            qa_status="VERIFIED",
            conflict_status="CONFLICT",
            evidence_status="UNKNOWN",
        )
    )
    db.commit()
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-CLAIM-001")
    assert knowledge.manufacturer_claims is None
