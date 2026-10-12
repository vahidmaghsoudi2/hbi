"""WP-INTAKE-CLAIM-INTEGRITY-001 — review-gap closure tests.

Covers items required by independent review of PR #353:
- EvidenceUpdate: omitted field vs explicit null vs blank
- claim_type × field × QA × conflict matrix for manufacturer destinations
- INFERENCE vs FACT distinction and evidence-row provenance
- Safe rebuild behavior with legacy unsupported claim_type rows (no rewrite)
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.claim_taxonomy import ALLOWED_CLAIM_TYPES, normalize_claim_type_value
from app.interface.schemas import EvidenceUpdate
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


def _product(db, product_id="P-REV-001"):
    db.add(
        Product(
            product_id=product_id,
            brand="ReviewBrand",
            product_name="Claim Integrity Review",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.commit()


def _ev(
    db,
    *,
    product_id,
    evidence_id,
    field,
    claim,
    claim_type,
    qa_status="VERIFIED",
    conflict_status="NONE",
    source_type="MANUFACTURER",
):
    db.add(
        Evidence(
            evidence_id=evidence_id,
            product_id=product_id,
            claim_id=f"C-{evidence_id}",
            field=field,
            claim=claim,
            claim_type=claim_type,
            source_type=source_type,
            source_reference=f"test://{evidence_id}",
            qa_status=qa_status,
            conflict_status=conflict_status,
            evidence_status="UNKNOWN",
        )
    )
    db.commit()


def test_evidence_update_omit_claim_type_does_not_force_value():
    """Omitted claim_type stays unset so callers using exclude_unset skip the column."""
    body = EvidenceUpdate.model_validate({})
    assert body.claim_type is None
    assert "claim_type" not in body.model_fields_set
    dumped = body.model_dump(exclude_unset=True)
    assert "claim_type" not in dumped


def test_evidence_update_explicit_null_claim_type_is_set_but_none():
    """Explicit JSON null is distinct from omission for exclude_unset dumps."""
    body = EvidenceUpdate.model_validate({"claim_type": None})
    assert body.claim_type is None
    assert "claim_type" in body.model_fields_set
    dumped = body.model_dump(exclude_unset=True)
    assert "claim_type" in dumped
    assert dumped["claim_type"] is None


def test_evidence_update_blank_claim_type_rejected():
    with pytest.raises(PydanticValidationError):
        EvidenceUpdate.model_validate({"claim_type": "   "})


def test_evidence_update_valid_claim_type_normalized():
    body = EvidenceUpdate.model_validate({"claim_type": "inference"})
    assert body.claim_type == "INFERENCE"
    assert "claim_type" in body.model_fields_set


def test_evidence_update_unsupported_claim_type_rejected():
    with pytest.raises(PydanticValidationError):
        EvidenceUpdate.model_validate({"claim_type": "BENEFIT"})


@pytest.mark.parametrize(
    "field,claim_type,qa_status,conflict_status,expect_mfg",
    [
        ("manufacturer_claim", "MANUFACTURER_CLAIM", "VERIFIED", "NONE", True),
        ("manufacturer_claims", "MANUFACTURER_CLAIM", "APPROVED", "NONE", True),
        ("claim", "MANUFACTURER_CLAIM", "VERIFIED", "NONE", True),
        ("manufacturer_claim", "FACT", "VERIFIED", "NONE", False),
        ("manufacturer_claim", "INFERENCE", "VERIFIED", "NONE", False),
        ("manufacturer_claim", "EVIDENCE", "VERIFIED", "NONE", False),
        ("manufacturer_claim", "UNKNOWN", "VERIFIED", "NONE", False),
        ("manufacturer_claim", "CONFLICT", "VERIFIED", "NONE", False),
        ("manufacturer_claims", "FACT", "VERIFIED", "NONE", False),
        ("claim", "FACT", "VERIFIED", "NONE", False),
        ("manufacturer_claim", "MANUFACTURER_CLAIM", "PENDING", "NONE", False),
        ("manufacturer_claim", "MANUFACTURER_CLAIM", "REJECTED", "NONE", False),
        ("manufacturer_claim", "MANUFACTURER_CLAIM", "VERIFIED", "CONFLICT", False),
    ],
)
def test_manufacturer_destination_matrix(
    db, field, claim_type, qa_status, conflict_status, expect_mfg
):
    pid = f"P-MX-{field[:4]}-{claim_type[:4]}-{qa_status[:3]}-{conflict_status[:3]}"
    eid = f"E-{pid}"
    _product(db, product_id=pid)
    source = "PEER_REVIEWED" if claim_type == "FACT" else "MANUFACTURER"
    _ev(
        db,
        product_id=pid,
        evidence_id=eid,
        field=field,
        claim="matrix-token",
        claim_type=claim_type,
        qa_status=qa_status,
        conflict_status=conflict_status,
        source_type=source,
    )
    knowledge = ProductKnowledgeService(db).update_from_evidence(pid)
    if expect_mfg:
        assert knowledge.manufacturer_claims is not None
        assert "matrix-token" in knowledge.manufacturer_claims
    else:
        assert knowledge.manufacturer_claims is None


def test_inference_and_fact_rows_preserve_claim_type_on_create(db):
    _product(db)
    svc = EvidenceService(db)
    inference = svc.add_evidence(
        {
            "product_id": "P-REV-001",
            "claim": "likely hydrating",
            "source_type": "MANUFACTURER",
            "source_reference": "test://inference",
            "claim_type": "INFERENCE",
            "field": "claimed_benefits",
        },
        actor_id="tester",
        actor_role="Admin",
    )
    fact = svc.add_evidence(
        {
            "product_id": "P-REV-001",
            "claim": "peer-reviewed hydration",
            "source_type": "PEER_REVIEWED",
            "source_reference": "test://fact",
            "claim_type": "FACT",
            "field": "claimed_benefits",
        },
        actor_id="tester",
        actor_role="Admin",
    )
    assert inference.claim_type == "INFERENCE"
    assert fact.claim_type == "FACT"
    assert inference.claim_type != fact.claim_type

    # Evidence provenance remains attached to each typed row after service persistence.
    assert inference.source_reference == "test://inference"
    assert fact.source_reference == "test://fact"
    assert inference.product_id == fact.product_id == "P-REV-001"
    persisted_inference = db.query(Evidence).filter_by(evidence_id=inference.evidence_id).one()
    persisted_fact = db.query(Evidence).filter_by(evidence_id=fact.evidence_id).one()
    assert persisted_inference.claim_type == "INFERENCE"
    assert persisted_fact.claim_type == "FACT"
    assert persisted_inference.source_reference == "test://inference"
    assert persisted_fact.source_reference == "test://fact"


def test_fact_never_silently_becomes_manufacturer_claim_in_knowledge(db):
    _product(db)
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-FACT-MFG",
        field="manufacturer_claim",
        claim="should-not-be-mfg",
        claim_type="FACT",
        source_type="PEER_REVIEWED",
    )
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-INF-MFG",
        field="manufacturer_claims",
        claim="also-not-mfg",
        claim_type="INFERENCE",
    )
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-REV-001")
    assert knowledge.manufacturer_claims is None


def test_inference_approved_can_populate_claimed_benefits_without_becoming_fact(db):
    """Field-based benefit mapping is independent of claim_type; row type stays INFERENCE."""
    _product(db)
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-INF-BEN",
        field="claimed_benefits",
        claim="inferred-benefit",
        claim_type="INFERENCE",
    )
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-REV-001")
    assert knowledge.claimed_benefits is not None
    assert "inferred-benefit" in knowledge.claimed_benefits
    row = db.query(Evidence).filter_by(evidence_id="E-INF-BEN").one()
    assert row.claim_type == "INFERENCE"


def test_legacy_unsupported_claim_type_row_does_not_crash_or_enter_manufacturer(db):
    """Pre-existing unsupported values are not rewritten; they never enter manufacturer_claims."""
    _product(db)
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-LEGACY-BENEFIT",
        field="manufacturer_claim",
        claim="legacy-benefit-token",
        claim_type="BENEFIT",
    )
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-REV-001")
    assert knowledge.manufacturer_claims is None
    row = db.query(Evidence).filter_by(evidence_id="E-LEGACY-BENEFIT").one()
    assert row.claim_type == "BENEFIT"


def test_legacy_unsupported_type_does_not_block_valid_manufacturer_row(db):
    _product(db)
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-LEGACY",
        field="manufacturer_claim",
        claim="legacy-noise",
        claim_type="BENEFIT",
    )
    _ev(
        db,
        product_id="P-REV-001",
        evidence_id="E-VALID-MFG",
        field="manufacturer_claim",
        claim="valid-mfg",
        claim_type="MANUFACTURER_CLAIM",
    )
    knowledge = ProductKnowledgeService(db).update_from_evidence("P-REV-001")
    assert knowledge.manufacturer_claims is not None
    assert "valid-mfg" in knowledge.manufacturer_claims
    assert "legacy-noise" not in knowledge.manufacturer_claims


def test_normalize_helper_documents_update_null_semantics():
    assert normalize_claim_type_value(None, missing_default=None) is None
    assert normalize_claim_type_value(None, missing_default="UNKNOWN") == "UNKNOWN"
    assert normalize_claim_type_value("fact", missing_default=None) == "FACT"
    with pytest.raises(ValueError):
        normalize_claim_type_value("BENEFIT", missing_default=None)
