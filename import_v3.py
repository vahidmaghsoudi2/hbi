from app.database import SessionLocal
from app.models.evidence import Evidence
from datetime import datetime

db = SessionLocal()

# First, check existing evidence_ids to understand the pattern
print("=== Existing Evidence IDs ===")
existing = db.query(Evidence).all()
for ev in existing[:5]:
    print(f"  {ev.evidence_id} | {ev.product_id[:30]}...")
print(f"  ... total: {len(existing)}")
print()

# Determine next sequence numbers
max_a = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FUSION-WATER-MAGIC-50").count()
max_b = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").count()
print(f"Product A existing: {max_a}, Product B existing: {max_b}")
print()

new_evidence = [
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "Full INCI list with Porphyridium Cruentum Extract, Hyaluronic Acid, Tocopherol", "field": "ingredients", "claim_type": "FACT", "source_reference": "https://incidecoder.com/products/isdin-fusion-water-magic-spf-50-2", "source_type": "REPUTABLE_RETAILER", "source_date": "2023-04-01", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Full INCI from INCIDecoder"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "Key ingredients: Mediterranean Algae Extract, Hyaluronic Acid, Vitamin E", "field": "ingredients", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/fotoprotector-isdin/magic-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2025-11-13", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Manufacturer highlights key actives"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "Ultralight facial sunscreen with immediate absorption for daily use", "field": "texture", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://incidecoder.com/products/isdin-fusion-water-magic-spf-50-2", "source_type": "REPUTABLE_RETAILER", "source_date": "2023-04-01", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Texture claim from INCIDecoder"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "12-hour hydration (33 subjects, 28 days)", "field": "clinical_evidence", "claim_type": "EVIDENCE_SUPPORTED", "source_reference": "https://www.isdin.com/us/p/fusion-water-magic/4750", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "US", "notes": "Clinical study claim"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "Non-comedogenic, mineral oil free, oil control", "field": "formulation", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/mx/p/fusion-water-magic-spf-50/1349", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Middle East", "notes": "Formulation claims"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "SPF 50 offers 3x minimum UVB protection", "field": "spf_rating", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/es-PE/bloqueador-solar/manchas-solares/", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Latin America", "notes": "SPF marketing claim"},
    {"product_id": "ISDIN-FUSION-WATER-MAGIC-50", "short": "A", "claim": "Suitable for all skin types including sensitive and atopic", "field": "testing_claims", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/mx/p/fusion-water-magic-spf-50/1349", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Middle East", "notes": "Tolerance claim"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "Full INCI with Niacinamide, Phenylethyl Resorcinol, Panthenol", "field": "ingredients", "claim_type": "FACT", "source_reference": "https://incidecoder.com/products/isdin-fotoultra-100-active-unify-color-spf-50", "source_type": "REPUTABLE_RETAILER", "source_date": "2024-06-15", "evidence_strength": "MODERATE", "market_region": "Global", "notes": "Full INCI from INCIDecoder"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "Key actives: Niacinamide, Phenylethyl Resorcinol, Panthenol, Allantoin", "field": "ingredients", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Manufacturer actives list"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "Triple depigmenting action clears and unifies skin tone", "field": "benefits", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Core benefit claim"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "DP3-Unify complex regulates melanin production", "field": "formulation", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Proprietary complex"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "Tinted formula evens skin tone with natural finish", "field": "texture", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.lovelyskin.com/o/isdin-fotoultra-100-active-unify-color-spf-50", "source_type": "REPUTABLE_RETAILER", "source_date": "2026-05-11", "evidence_strength": "MODERATE", "market_region": "US", "notes": "Retailer description"},
    {"product_id": "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", "short": "B", "claim": "SPF 50+ twice minimum UVA protection for pigmentation", "field": "spf_rating", "claim_type": "MANUFACTURER_CLAIM", "source_reference": "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50", "source_type": "OFFICIAL_MANUFACTURER", "source_date": "2026-08-18", "evidence_strength": "MODERATE", "market_region": "Europe", "notes": "Technical SPF claim"}
]

created = 0
skipped = 0
failed = 0
seq_a = max_a
seq_b = max_b

print("=== Importing Evidence (v3 - with evidence_id) ===")
print("=" * 60)

for i, ev_data in enumerate(new_evidence, 1):
    pid = ev_data["product_id"]
    short = ev_data["short"]
    
    # Generate evidence_id
    if short == "A":
        seq_a += 1
        evidence_id = f"EV-A-{seq_a:03d}"
    else:
        seq_b += 1
        evidence_id = f"EV-B-{seq_b:03d}"
    
    # Generate claim_id
    claim_id = f"EV-{pid}-{seq_a if short == 'A' else seq_b}"
    
    # Check duplicate by claim text
    existing = db.query(Evidence).filter(
        Evidence.product_id == pid,
        Evidence.claim == ev_data["claim"]
    ).first()
    
    if existing:
        print(f"{i:2d}. SKIP (duplicate): {evidence_id}")
        skipped += 1
        continue
    
    try:
        ev = Evidence(
            evidence_id=evidence_id,
            claim_id=claim_id,
            product_id=pid,
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
            qa_status="VERIFIED",
            evidence_status="SUPPORTED",
            conflict_status="NONE"
        )
        db.add(ev)
        db.commit()
        created += 1
        print(f"{i:2d}. OK: {evidence_id} | {ev_data['field']}")
    except Exception as e:
        db.rollback()
        failed += 1
        print(f"{i:2d}. FAIL: {evidence_id} | {str(e)[:60]}")

print()
print("=" * 60)
total_a = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FUSION-WATER-MAGIC-50").count()
total_b = db.query(Evidence).filter(Evidence.product_id == "ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").count()
print(f"Created: {created} | Skipped: {skipped} | Failed: {failed}")
print(f"Product A total: {total_a} (was 4)")
print(f"Product B total: {total_b} (was 6)")
print(f"Grand total: {total_a + total_b}")
db.close()
