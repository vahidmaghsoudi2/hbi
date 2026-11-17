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


def test_seven_product_manifest_has_exact_canonical_scope_and_24_assertions():
    manifest = _manifest()
    products = manifest["products"]

    assert len(products) == 7
    assert {product["product_id"] for product in products} == CANONICAL_IDS
    assert sum(len(product["assertions"]) for product in products) == 24
    assert {
        product["dossier"]: len(product["assertions"])
        for product in products
    } == {"P1": 4, "P2": 4, "P3": 3, "P4": 3, "P5": 2, "P6": 3, "P7": 5}


def test_manifest_preserves_p7_ingredient_assertion_as_review_only():
    manifest = _manifest()
    p7 = next(product for product in manifest["products"] if product["dossier"] == "P7")
    ingredient_assertions = [
        assertion for assertion in p7["assertions"]
        if assertion.get("field") == "ingredients"
    ]

    assert len(ingredient_assertions) == 1
    boundary = manifest["acceptance_boundary"]
    assert boundary["draft_manifest_status"] == "RESEARCH_DRAFT_ONLY"
    assert boundary["product_qa"] == "UNCHANGED"
    assert boundary["product_identity"] == "UNCHANGED"
    assert boundary["inventory"] == "UNCHANGED"
    assert any("Resolve P7's two existing conflicting Evidence rows" in item
               for item in boundary["explicit_review_queue"])
