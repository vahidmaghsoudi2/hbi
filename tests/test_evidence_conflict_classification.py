"""Regression tests for conservative evidence-conflict classification."""
from app.models.evidence import Evidence
from app.models.product import Product
from app.services.evidence_service import EvidenceService


def _add_product_and_evidence(db_session, source_pairs):
    product_id = "P_CONFLICT_CLASSIFICATION_001"
    db_session.add(
        Product(
            product_id=product_id,
            brand="TestBrand",
            product_name="TestProduct",
            product_line="SKIN",
            identity_status="NEEDS_REVIEW",
            qa_verdict="PENDING",
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
                field="manufacturer_claims",
                claim_type="MANUFACTURER_CLAIM",
                evidence_status="UNKNOWN",
                conflict_status="CONFLICT",
                qa_status="PENDING",
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
