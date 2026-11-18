from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs"
    / "product-intake-knowledge-registry"
    / "SEVEN_PRODUCT_EVIDENCE_DRAFT_MANIFEST_V1.json"
)

CANONICAL_IDS = {
    "HBI-PROD-FE320FA135B843B6",
    "HBI-PROD-2CC249240D504453",
    "HBI-PROD-C29AA2F410A84CCA",
    "HBI-PROD-7F55ED88F41144F1",
    "HBI-PROD-96788ADC488942E3",
    "HBI-PROD-70EEE418BE0F4DAB",
    "HBI-PROD-22C55A8223A945A6",
}


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def test_seven_product_manifest_has_exact_canonical_scope_and_25_manufacturer_assertions():
    manifest = _manifest()
    products = manifest["products"]
    assertions = [
        assertion
        for product in products
        for assertion in product["assertions"]
    ]

    assert len(products) == 7
    assert {product["product_id"] for product in products} == CANONICAL_IDS
    assert len(assertions) == 25
    assert {
        product["dossier"]: len(product["assertions"])
        for product in products
    } == {"P1": 5, "P2": 4, "P3": 4, "P4": 4, "P5": 4, "P6": 0, "P7": 4}
    assert {item["source_type"] for item in assertions} == {"MANUFACTURER"}
    assert {item["claim_type"] for item in assertions} == {"MANUFACTURER_CLAIM"}
    assert all(item["evidence_strength"] == "UNVERIFIED" for item in assertions)
    assert all(item.get("source_reference") for item in assertions)


def test_manifest_preserves_p7_ingredient_assertion_and_existing_conflict_review_boundary():
    manifest = _manifest()
    p7 = next(product for product in manifest["products"] if product["dossier"] == "P7")
    ingredient_assertions = [
        assertion for assertion in p7["assertions"]
        if assertion.get("field") == "ingredients"
    ]

    assert len(ingredient_assertions) == 1
    boundary = manifest["acceptance_boundary"]
    assert boundary["draft_manifest_status"] == "MANUFACTURER_PACKAGE_SOURCE_DRAFT_ONLY"
    assert boundary["product_qa"] == "UNCHANGED"
    assert boundary["product_identity"] == "UNCHANGED"
    assert boundary["inventory"] == "UNCHANGED"
    assert any(
        "Keep the two existing Anua conflict rows" in item
        for item in boundary["explicit_review_queue"]
    )
    assert any(
        "do not infer a one-to-one match from counts" in item
        for item in boundary["explicit_review_queue"]
    )


def test_historical_clinique_claims_stay_unverified_when_official_url_redirects_to_replacement():
    manifest = _manifest()
    p6 = next(product for product in manifest["products"] if product["dossier"] == "P6")
    assert p6["assertions"] == []
    assert any("currently redirects to the current/replacement serum" in item for item in p6["identity_limits"])
    assert any("Keep historical claims and formula UNKNOWN" in item for item in manifest["acceptance_boundary"]["explicit_review_queue"])


def test_anua_redness_survey_claim_uses_the_exact_product_page():
    manifest = _manifest()
    p7 = next(product for product in manifest["products"] if product["dossier"] == "P7")
    claim = next(item for item in p7["assertions"] if item["field"] == "claimed_benefits")
    assert claim["source_reference"] == "https://anua.com/products/azelaic-acid-10-hyaluron-redness-soothing-serum"
    assert claim["claim_type"] == "MANUFACTURER_CLAIM"
