from app.database import SessionLocal
from app.models.evidence import Evidence
from datetime import datetime

db = SessionLocal()

new_evidence = [
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "Full INCI list with Porphyridium Cruentum Extract, Hyaluronic Acid, Tocopherol", "field": "ingredients", "claim_type": "FACT", "source_reference": "https://incidecoder.com/products/isdin-fusion-water-magic-spf-50-2", "source_type": "REPUTABLE_RETAILER", "source_date": "2023-04-01", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Full INCI from INCIDecoder. Patched source_type per Framework 1-B."},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "Key ingredients: Mediterranean Algae Extract (Porphyridium Cruentum), Hyaluronic Acid, Vitamin E", "field": "ingredients", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/fotoprotector-isdin/magic-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2025-11-13", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Manufacturer highlights key actives"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "Ultralight facial sunscreen with immediate absorption for daily use", "field": "texture", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://incidecoder.com/products/isdin-fusion-water-magic-spf-50-2", "source_type": "REPUTABLE_RETAILER", "source_date": "2023-04-01", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Texture claim from INCIDecoder"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "12-hour hydration (Evaluation in 33 subjects, results after 28 days)", "field": "clinical_evidence", "claim_type": "EVIDENCE_SUPPORTED", "source_reference": "https://www.isdin.com/us/p/fusion-water-magic/4750", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "US", "notes": "Clinical study claim, details not independently accessible"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "Non-comedogenic, mineral oil free, oil control", "field": "formulation", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/mx/p/fusion-water-magic-spf-50/1349", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Middle East", "notes": "Formulation claims from ISDIN Mexico"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "SPF 50 offers 3x the minimum protection required against UVB rays", "field": "spf_rating", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/es-PE/bloqueador-solar/manchas-solares/", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Latin America", "notes": "Marketing interpretation of SPF standard"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "claim": "Suitable for all skin types, including sensitive and atopic skin", "field": "testing_claims", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/mx/p/fusion-water-magic-spf-50/1349", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Middle East", "notes": "Tolerance claim from ISDIN Mexico"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "Full INCI list with Niacinamide, Phenylethyl Resorcinol, Panthenol, Iron Oxides", "field": "ingredients", "claim_type": "FACT", "source_reference": "https://incidecoder.com/products/isdin-fotoultra-100-active-unify-color-spf-50", "source_type": "REPUTABLE_RETAILER", "source_date": "2024-06-15", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Full INCI from INCIDecoder. Patched source_type per Framework 1-B."},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "Key ingredients: Niacinamide, Phenylethyl Resorcinol, Panthenol, Allantoin, Vitamin E", "field": "ingredients", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Manufacturer highlights depigmenting and soothing actives"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "Fluid facial sunscreen with triple depigmenting action that clears up and unifies skin tone", "field": "benefits", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Core benefit claim from ISDIN UK"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "Helps regulate melanin production thanks to the DP3-Unify complex", "field": "formulation", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Proprietary complex claim, no independent verification"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "Tinted formula evens skin tone and provides a natural finish", "field": "texture", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.lovelyskin.com/o/isdin-fotoultra-100-active-unify-color-spf-50", "source_type": "REPUTABLE_RETAILER", "source_date": "2026-05-11", "evidence_strength": "MODERATE", "market_region": "US", "notes": "Retailer description consistent with manufacturer claims"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "claim": "SPF 50+ provides twice the minimum protection required against UVA rays associated with pigmentation", "field": "spf_rating", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Technical SPF claim"}
]

created = 0
for ev_data in new_evidence:
    existing_count = db.query(Evidence).filter(Evidence.product_id == ev_data["product_id"]).count()
    claim_id = f"EV-{ev_data['product_id']}-{existing_count + 1}"
    existing = db.query(Evidence).filter(Evidence.product_id == ev_data["product_id"], Evidence.source_reference == ev_data["source_reference"]).first()
    if existing:
        print(f"SKIPPED (duplicate): {claim_id}")
        continue
    ev = Evidence(
        claim_id=claim_id,
        product_id=ev_data["product_id"],
        claim=ev_data["claim"],
        field=ev_data["field"],
        claim_type=ev_data["claim_type"],
        source_reference=ev_data["source_reference"],
        source_type=ev_data["source_type"],
        source_date=ev_data["source_date"],
        evidence_date=datetime.now(),
        evidence_strength=ev_data["evidence_strength"],
        market_region=ev_data["market_region"],
        notes=ev_data["notes"],
        qa_status="VERIFIED"
    )
    db.add(ev)
    created += 1
    print(f"CREATED: {claim_id}")

db.commit()

total_a = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FUSION-WATER-MAGIC-50").count()
total_b = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").count()
print(f"\nSummary:")
print(f"Created: {created}")
print(f"Product A total: {total_a}")
print(f"Product B total: {total_b}")
db.close()
