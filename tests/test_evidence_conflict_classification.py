"""Regression tests for conservative evidence-conflict classification."""
import pytest

from app.core.exceptions import ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.services.evidence_service import EvidenceService


def _add_product_and_evidence(db_session, source_pairs, product_market=None):
    product_id = "P_CONFLICT_CLASSIFICATION_001"
    db_session.add(
        Product(
            product_id=product_id,
            brand="TestBrand",
            product_name="TestProduct",
            product_line="SKIN",
            identity_status="NEEDS_REVIEW",
            qa_verdict="PENDING",
            market_region=product_market,
        )
    )
    for index, item in enumerate(source_pairs, start=1):
        db_session.add(
            Evidence(
                evidence_id=f"EV-CONFLICT-CLASS-{index}",
                product_id=product_id,
                claim_id=f"CL-CONFLICT-CLASS-{index}",
                source_type=item["source_type"],
                source_reference=item["source_reference"],
                claim=item["claim"],
                field=item.get("field", "manufacturer_claims"),
                claim_type="MANUFACTURER_CLAIM",
                evidence_status="UNKNOWN",
                conflict_status="CONFLICT",
                qa_status="PENDING",
                market_region=item.get("market_region"),
            )
        )
    db_session.commit()
    return product_id


def test_same_source_paraphrase_is_review_required_not_confirmed_high_conflict(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The manufacturer presents the product as featuring NAD+ and 50 types of peptides.",
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product/",
                "claim": "The manufacturer describes the product as containing NAD+ and 50 peptide types.",
            },
        ],
    )

    conflicts = EvidenceService(db_session).detect_conflicts(product_id)

    assert len(conflicts) == 1
    assert conflicts[0]["severity"] == "REVIEW_REQUIRED"
    assert conflicts[0]["status"] == "NEEDS_REVIEW"
    # Classification changes, but persisted CONFLICT remains a downstream block.
    rows = db_session.query(Evidence).filter(Evidence.product_id == product_id).all()
    assert all(row.conflict_status == "CONFLICT" for row in rows)


def test_different_sources_with_different_claims_remain_high_unresolved(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://manufacturer.example/product",
                "claim": "The product contains 50 peptide types.",
            },
            {
                "source_type": "INDEPENDENT_REVIEW",
                "source_reference": "https://review.example/product",
                "claim": "The product contains 20 peptide types.",
            },
        ],
    )

    conflicts = EvidenceService(db_session).detect_conflicts(product_id)

    assert len(conflicts) == 1
    assert conflicts[0]["severity"] == "HIGH"
    assert conflicts[0]["status"] == "UNRESOLVED"

def test_missing_source_reference_cannot_be_classified_as_same_source(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "",
                "claim": "The product features NAD+.",
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "",
                "claim": "The product features NAD+ and peptides.",
            },
        ],
    )

    conflicts = EvidenceService(db_session).detect_conflicts(product_id)

    assert len(conflicts) == 1
    assert conflicts[0]["severity"] == "HIGH"
    assert conflicts[0]["status"] == "UNRESOLVED"

def test_facade_preserves_same_source_classification_in_conflict_dto(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The manufacturer presents the product as featuring NAD+.",
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product/",
                "claim": "The manufacturer describes the product as featuring NAD+.",
            },
        ],
    )

    from app.interface.facades import EvidenceFacade

    conflicts = EvidenceFacade(db_session).detect_conflicts(product_id)

    assert len(conflicts) == 1
    assert conflicts[0].severity == "REVIEW_REQUIRED"
    assert conflicts[0].status == "NEEDS_REVIEW"
    rows = db_session.query(Evidence).filter(Evidence.product_id == product_id).all()
    assert all(row.conflict_status == "CONFLICT" for row in rows)



def test_conflicts_are_scoped_to_market_region(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The formula contains ingredient A.",
                "market_region": None,
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The US formula contains ingredient B.",
                "market_region": "US",
            },
        ],
    )

    assert EvidenceService(db_session).detect_conflicts(product_id) == []


def test_pending_evidence_field_reclassification_is_audited_and_preserves_governance(db_session):
    from app.models.evidence_mutation_log import EvidenceMutationLog

    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The manufacturer states the product contains 10% active X.",
                "field": "ingredients",
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The manufacturer's INCI declaration lists active X.",
                "field": "ingredients",
            },
        ],
    )

    result = EvidenceService(db_session).reclassify_field(
        "EV-CONFLICT-CLASS-1",
        "manufacturer_claims",
        "Separate the manufacturer concentration statement from the INCI declaration.",
        actor_id="po-user",
        actor_role="PRODUCT_OWNER",
    )

    rows = db_session.query(Evidence).filter(Evidence.product_id == product_id).all()
    by_id = {row.evidence_id: row for row in rows}
    assert result.field == "manufacturer_claims"
    assert by_id["EV-CONFLICT-CLASS-2"].field == "ingredients"
    assert all(row.conflict_status == "NONE" for row in rows)
    assert all(row.qa_status == "PENDING" for row in rows)
    assert all(row.evidence_status == "UNKNOWN" for row in rows)

    audit_rows = (
        db_session.query(EvidenceMutationLog)
        .filter(EvidenceMutationLog.product_id == product_id)
        .all()
    )
    assert len(audit_rows) == 2
    assert {row.action for row in audit_rows} == {
        "RECLASSIFY_FIELD", "RECLASSIFY_CONFLICT_STATE"
    }
    assert all(row.reason for row in audit_rows)

    import json
    field_audit = next(row for row in audit_rows if row.action == "RECLASSIFY_FIELD")
    assert json.loads(field_audit.diff)["field"] == {
        "old": "ingredients",
        "new": "manufacturer_claims",
    }

def test_resolving_conflict_does_not_reject_other_market_evidence(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/us",
                "claim": "The US formula contains ingredient A.",
                "field": "ingredients",
                "market_region": None,
            },
            {
                "source_type": "INDEPENDENT_REVIEW",
                "source_reference": "https://review.example/us",
                "claim": "The US formula contains ingredient B.",
                "field": "ingredients",
                "market_region": "us",
            },
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/eu",
                "claim": "The EU formula contains ingredient C.",
                "field": "ingredients",
                "market_region": "EU",
            },
        ],
        product_market="US",
    )

    selected = EvidenceService(db_session).resolve_conflict(
        "EV-CONFLICT-CLASS-1",
        "US-market claim selected for this test.",
        actor_id="qa-user",
        actor_role="Reviewer/QA",
    )

    rows = db_session.query(Evidence).filter(Evidence.product_id == product_id).all()
    by_id = {row.evidence_id: row for row in rows}

    assert selected.conflict_status == "NONE"
    assert selected.qa_status == "PENDING"
    assert by_id["EV-CONFLICT-CLASS-2"].conflict_status == "NONE"
    assert by_id["EV-CONFLICT-CLASS-2"].qa_status == "REJECTED"
    assert by_id["EV-CONFLICT-CLASS-3"].conflict_status == "CONFLICT"
    assert by_id["EV-CONFLICT-CLASS-3"].qa_status == "PENDING"



def test_unscoped_evidence_inherits_product_market_for_conflict_detection(db_session):
    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/unscoped",
                "claim": "The formula contains ingredient A.",
                "field": "ingredients",
                "market_region": None,
            },
            {
                "source_type": "INDEPENDENT_REVIEW",
                "source_reference": "https://review.example/us",
                "claim": "The formula contains ingredient B.",
                "field": "ingredients",
                "market_region": "us",
            },
        ],
        product_market="US",
    )

    conflicts = EvidenceService(db_session).detect_conflicts(product_id)

    assert len(conflicts) == 1
    assert conflicts[0]["field"] == "ingredients"
    assert conflicts[0]["market_region"] == "US"
    assert set(conflicts[0]["evidence_ids"]) == {
        "EV-CONFLICT-CLASS-1",
        "EV-CONFLICT-CLASS-2",
    }

def test_reclassification_rejects_unknown_target_field_without_mutation_or_audit(db_session):
    from app.models.evidence_mutation_log import EvidenceMutationLog

    product_id = _add_product_and_evidence(
        db_session,
        [
            {
                "source_type": "MANUFACTURER_WEBSITE",
                "source_reference": "https://example.test/product",
                "claim": "The product has an unsupported custom field claim.",
                "field": "ingredients",
            },
        ],
    )

    with pytest.raises(ValidationError, match="Unsupported target field"):
        EvidenceService(db_session).reclassify_field(
            "EV-CONFLICT-CLASS-1",
            "unreviewed_custom_field",
            "This target is intentionally outside the supported taxonomy.",
            actor_id="po-user",
            actor_role="PRODUCT_OWNER",
        )

    row = db_session.query(Evidence).filter(
        Evidence.evidence_id == "EV-CONFLICT-CLASS-1"
    ).one()
    assert row.field == "ingredients"
    assert row.conflict_status == "CONFLICT"
    assert row.qa_status == "PENDING"
    assert row.evidence_status == "UNKNOWN"
    assert db_session.query(EvidenceMutationLog).filter(
        EvidenceMutationLog.product_id == product_id
    ).count() == 0

