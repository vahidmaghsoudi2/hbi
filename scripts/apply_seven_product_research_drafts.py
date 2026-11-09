#!/usr/bin/env python3
"""Apply the seven-product source-bound research manifest as PENDING Evidence drafts.

This script never creates or edits Product Master rows and never verifies Evidence.
Dry-run is the default. Pass --apply to write through the authenticated ResearchDraft API.
The pilot operator token endpoint is development/pilot only and is disabled in production.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CANONICAL_IDS = {
    "HBI-PROD-FE320FA135B843B6",
    "HBI-PROD-2CC249240D504453",
    "HBI-PROD-C29AA2F410A84CCA",
    "HBI-PROD-7F55ED88F41144F1",
    "HBI-PROD-96788ADC488942E3",
    "HBI-PROD-70EEE418BE0F4DAB",
    "HBI-PROD-22C55A8223A945A6",
}
KNOWLEDGE_CONTENT_FIELDS = (
    "ingredients", "ingredient_roles", "claimed_benefits", "known_use_cases",
    "contraindications", "usage_instructions", "manufacturer_claims",
    "other_attributes", "evidence_refs",
)


def request_json(url: str, *, method: str = "GET", token: str | None = None,
                 payload: dict | None = None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot reach HBI API at {url}: {exc}") from exc


def knowledge_snapshot(api: str, token: str, product_id: str) -> dict:
    encoded = urllib.parse.quote(product_id, safe="")
    return request_json(f"{api}/evidence/knowledge/{encoded}", token=token)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--manifest", default=str(
        Path(__file__).resolve().parent.parent
        / "docs/product-intake-knowledge-registry/SEVEN_PRODUCT_EVIDENCE_DRAFT_MANIFEST_V1.json"
    ))
    parser.add_argument("--apply", action="store_true", help="Write PENDING drafts. Without this flag, only preview.")
    args = parser.parse_args()
    api = args.api_base.rstrip("/")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8-sig"))
    products = manifest.get("products", [])
    ids = {p.get("product_id") for p in products}
    if len(products) != 7 or ids != CANONICAL_IDS:
        raise RuntimeError("Manifest must contain exactly the seven approved canonical Product IDs.")

    print(f"Mode: {'APPLY PENDING DRAFTS' if args.apply else 'DRY RUN'}")
    print(f"API: {api}")
    print(f"Products: {len(products)}")
    print(f"Assertions in manifest: {sum(len(p.get('assertions', [])) for p in products)}")

    if not args.apply:
        for product in products:
            print(f"- {product['dossier']} {product['product_id']}: {len(product['assertions'])} assertions")
        print("No API calls or database writes performed. Re-run with --apply to stage PENDING drafts.")
        return 0

    token_data = request_json(f"{api}/auth/pilot-operator-token", method="POST")
    token = token_data.get("access_token") if isinstance(token_data, dict) else None
    if not token:
        raise RuntimeError("Pilot operator token endpoint returned no access_token.")

    existing_products = request_json(f"{api}/products/manage", token=token)
    existing_ids = {p.get("product_id") for p in existing_products}
    missing = sorted(CANONICAL_IDS - existing_ids)
    if missing:
        raise RuntimeError(f"Refusing to write: canonical Product rows missing: {missing}")
    wrong_line = [
        p.get("product_id") for p in existing_products
        if p.get("product_id") in CANONICAL_IDS and p.get("product_line") != "SKIN"
    ]
    if wrong_line:
        raise RuntimeError(f"Refusing to write: canonical records are not SKIN products: {wrong_line}")

    plans = []
    before_knowledge = {}
    for product in products:
        pid = product["product_id"]
        encoded = urllib.parse.quote(pid, safe="")
        evidence = request_json(f"{api}/evidence/?product_id={encoded}", token=token)
        before_knowledge[pid] = knowledge_snapshot(api, token, pid)
        existing = {
            (row.get("field"), row.get("source_reference"), row.get("claim"))
            for row in evidence
        }
        pending = []
        for assertion in product.get("assertions", []):
            # P7 already has two conflicting source rows in ingredients.
            # Do not add another assertion to that disputed field automatically.
            if product["dossier"] == "P7" and assertion.get("field") == "ingredients":
                print(f"SKIP {pid} ingredients: existing conflict requires authorized reclassification.")
                continue
            key = (
                assertion.get("field"),
                assertion.get("source_reference"),
                assertion.get("claim"),
            )
            if key in existing:
                print(f"SKIP duplicate {pid} field={assertion.get('field')}")
                continue
            pending.append(assertion)
        plans.append((product, pending))

    total_written = 0
    written_ids = {}
    for product, assertions in plans:
        if not assertions:
            print(f"NO-OP {product['dossier']} {product['product_id']}: no new drafts")
            continue
        pid = product["product_id"]
        encoded = urllib.parse.quote(pid, safe="")
        saved = request_json(
            f"{api}/products/{encoded}/research-draft",
            method="POST",
            token=token,
            payload={"assertions": assertions},
        )
        if not isinstance(saved, list) or len(saved) != len(assertions):
            raise RuntimeError(f"{product['dossier']}: API did not return all newly created Evidence rows.")
        for row in saved:
            if row.get("product_id") != pid:
                raise RuntimeError(f"{product['dossier']}: returned Evidence is attached to the wrong Product ID.")
            if row.get("qa_status") != "PENDING" or row.get("evidence_status") != "UNKNOWN":
                raise RuntimeError(f"{product['dossier']}: draft status boundary was not preserved.")
        written_ids[pid] = [row.get("evidence_id") for row in saved]
        total_written += len(saved)
        print(f"STAGED {product['dossier']} {pid}: {len(saved)} PENDING Evidence rows")

    # Read back and prove no ProductKnowledge content was promoted by PENDING drafts.
    for product, _assertions in plans:
        pid = product["product_id"]
        encoded = urllib.parse.quote(pid, safe="")
        evidence_after = request_json(f"{api}/evidence/?product_id={encoded}", token=token)
        actual_ids = {row.get("evidence_id") for row in evidence_after}
        for evidence_id in written_ids.get(pid, []):
            if evidence_id not in actual_ids:
                raise RuntimeError(f"{product['dossier']}: Evidence read-back missing {evidence_id}.")
        after_knowledge = knowledge_snapshot(api, token, pid)
        before = before_knowledge[pid]
        changed = [field for field in KNOWLEDGE_CONTENT_FIELDS if after_knowledge.get(field) != before.get(field)]
        if changed:
            raise RuntimeError(
                f"{product['dossier']}: PENDING drafts unexpectedly populated ProductKnowledge content fields: {changed}"
            )
        if product["dossier"] == "P7" and after_knowledge.get("evidence_status") not in ("CONFLICT", "UNKNOWN", None):
            raise RuntimeError("P7: existing Evidence conflict was not preserved as a non-approved state.")

    print(f"COMPLETE: {total_written} new PENDING Evidence drafts written and read back.")
    print("No ProductKnowledge content was populated from PENDING drafts. Existing P7 conflict status may be refreshed by the service; Product Master, QA, lifecycle and inventory are not promoted or edited.")
    print("Next gate: explicit human Evidence QA, then authorized ProductKnowledge rebuild/read-back.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
