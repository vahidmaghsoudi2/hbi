from app.database import SessionLocal
from app.models.evidence import Evidence
from datetime import datetime

db = SessionLocal()

# فقط یک رکورد تست برای ریشه‌یابی
test_record = {
    "product_id": "ISDIN-FUSION-WATER-MAGIC-50",
    "claim": "TEST: Full INCI list with Porphyridium Cruentum Extract",
    "field": "ingredients",
    "claim_type": "FACT",
    "source_reference": "https://incidecoder.com/products/isdin-fusion-water-magic-spf-50-2",
    "source_type": "REPUTABLE_RETAILER",
    "source_date": "2023-04-01",
    "evidence_strength": "MODERATE",
    "market_region": "Global",
    "notes": "DEBUG TEST"
}

pid = test_record["product_id"]
max_id = db.query(Evidence).filter(Evidence.product_id == pid).count()
claim_id = f"EV-{pid}-{max_id + 1}"

print(f"Attempting to create: {claim_id}")
print(f"Product: {pid}")
print(f"Current count: {max_id}")
print(f"Claim: {test_record['claim'][:50]}...")
print()

try:
    ev = Evidence(
        claim_id=claim_id,
        product_id=pid,
        claim=test_record["claim"],
        field=test_record["field"],
        claim_type=test_record["claim_type"],
        source_reference=test_record["source_reference"],
        source_type=test_record["source_type"],
        source_date=test_record["source_date"],
        evidence_date=datetime.now(),
        evidence_strength=test_record["evidence_strength"],
        market_region=test_record["market_region"],
        notes=test_record["notes"],
        qa_status="VERIFIED"
    )
    db.add(ev)
    db.commit()
    print("SUCCESS: Record created and committed")
    
    # بررسی فوری
    verify = db.query(Evidence).filter(Evidence.claim_id == claim_id).first()
    if verify:
        print(f"VERIFIED: {verify.claim_id} exists in DB")
    else:
        print("ERROR: Commit succeeded but record not found")
        
except Exception as e:
    db.rollback()
    print(f"FAILED: {type(e).__name__}")
    print(f"Error: {str(e)}")
    print()
    print("Possible causes:")
    print("  1. NOT NULL constraint on a field")
    print("  2. Unique constraint violation")
    print("  3. Foreign key violation")
    print("  4. Database locked (SQLite)")
    print("  5. Column name mismatch with model")

db.close()
