"""Disposable end-to-end API test for the temporary numbuzin intake candidate.

This test uses the shared in-memory SQLite fixture. It must never seed data/seed_products.json
or any production database. The candidate and all evidence are discarded by fixture teardown.
"""
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.evidence import Evidence


PRODUCT_ID = "TEST-NB9-NAD-BIO-LIFTING-SIL-ESSENCE-50ML"


def test_temporary_numbuzin_candidate_intake_is_draft_and_disposable(client, db_session):
    # Obtain the repository's non-production scoped operator token.
    token_response = client.post("/api/v1/auth/pilot-operator-token")
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    identity = {
        "product_id": PRODUCT_ID,
        "brand": "numbuzin",
        "product_name": "No.9 NAD+ BIO Lifting-sil Essence, 50 mL",
        "product_line": "SKIN",
        "variant": "essence",
        "size_value": 50,
        "size_unit": "ml",
        "barcode_gtin": None,
        "market_region": None,
        "packaging_version": None,
    }

    # Run the existing duplicate check before create; no barcode is guessed.
    duplicate = client.post(
        "/api/v1/products/duplicate-check/",
        json=identity,
        headers=headers,
    )
    assert duplicate.status_code == 200, duplicate.text
    duplicate_result = duplicate.json()
    assert duplicate_result["result"] == "NEW", duplicate_result

    created = client.post("/api/v1/products/", json=identity, headers=headers)
    assert created.status_code == 201, created.text
    row = created.json()
    assert row["product_id"] == PRODUCT_ID
    # The API response schema intentionally omits lifecycle/governance fields.
    # Verify those fields through persisted ORM readback below instead.
    assert row.get("barcode_gtin") in (None, "")

    # Read back through the API, not only the POST response.
    readback = client.get(f"/api/v1/products/{PRODUCT_ID}")
    assert readback.status_code == 200, readback.text
    persisted = readback.json()
    assert persisted["product_id"] == PRODUCT_ID
    assert persisted.get("barcode_gtin") in (None, "")

    # Stock ledger anchor must not imply physical stock.
    inventory = db_session.query(Inventory).filter_by(product_id=PRODUCT_ID).one()
    assert inventory.quantity_available == 0
    assert inventory.quantity_reserved == 0
    assert inventory.stock_status == "OUT_OF_STOCK"

    # Record source-attributed research assertions; they remain unapproved.
    research = client.post(
        f"/api/v1/products/{PRODUCT_ID}/research-draft",
        headers=headers,
        json={
            "assertions": [
                {
                    "claim": "The official brand webpage displays the product name and nominal size as No.9 NAD+ BIO Lifting-sil Essence, 50 mL.",
                    "source_type": "MANUFACTURER",
                    "source_reference": "https://us.numbuzin.com/products/no-9-nad-bio-lifting-sil-essence",
                    "claim_type": "MANUFACTURER_CLAIM",
                    "field": "product_identity_webpage",
                    "market_region": "US_WEBPAGE",
                    "notes": "Webpage display only; does not verify a physical unit or its market variant.",
                },
                {
                    "claim": "The brand claims the product was clinically tested to reduce 11 types of wrinkles in four weeks; underlying study report and methods are not present in this test dossier.",
                    "source_type": "MANUFACTURER",
                    "source_reference": "https://us.numbuzin.com/products/no-9-nad-bio-lifting-sil-essence",
                    "claim_type": "MANUFACTURER_CLAIM",
                    "field": "claimed_benefits",
                    "market_region": "US_WEBPAGE",
                    "notes": "Manufacturer claim only; no independent efficacy conclusion.",
                },
                {
                    "claim": "GTIN/barcode, exact package market version, lot/batch, and expiry/PAO for a physical unit are not verified.",
                    "source_type": "OPERATOR_DECLARATION",
                    "source_reference": "HBI-TEST-DOSSIER-NB9",
                    "claim_type": "UNKNOWN",
                    "field": "identity_metadata",
                    "notes": "Explicit unknowns; do not infer values from third-party listings.",
                },
            ]
        },
    )
    assert research.status_code == 200, research.text
    evidence_rows = research.json()
    assert len(evidence_rows) == 3
    assert {r["claim_type"] for r in evidence_rows} == {
        "MANUFACTURER_CLAIM", "UNKNOWN"
    }
    assert all(r.get("qa_status") in (None, "PENDING") for r in evidence_rows)
    assert all(r.get("evidence_status") in (None, "PENDING", "UNKNOWN") for r in evidence_rows)

    # Persisted evidence readback confirms provenance and claim-type integrity.
    evidence_readback = client.get(
        "/api/v1/evidence/",
        params={"product_id": PRODUCT_ID},
        headers=headers,
    )
    assert evidence_readback.status_code == 200, evidence_readback.text
    persisted_evidence = evidence_readback.json()
    assert len(persisted_evidence) == 3
    assert {r["claim_type"] for r in persisted_evidence} == {
        "MANUFACTURER_CLAIM", "UNKNOWN"
    }
    assert all(r["product_id"] == PRODUCT_ID for r in persisted_evidence)

    # Explicitly confirm no approval/activation was performed.
    product_db_row = db_session.query(Product).filter_by(product_id=PRODUCT_ID).one()
    assert product_db_row.status == "DRAFT"
    assert product_db_row.identity_status == "NEEDS_REVIEW"
    assert product_db_row.qa_verdict == "PENDING"
    assert db_session.query(Evidence).filter_by(product_id=PRODUCT_ID).count() == 3
