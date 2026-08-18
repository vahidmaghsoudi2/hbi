from app.database import SessionLocal
from app.models.evidence import Evidence
from sqlalchemy import inspect
from datetime import datetime

db = SessionLocal()

print("=== STEP 1: Evidence Model Schema ===")
print("=" * 60)
mapper = inspect(Evidence)
for col in mapper.columns:
    nullable = "NULL allowed" if col.nullable else "NOT NULL"
    has_default = "has-default" if col.default is not None else "no-default"
    print(f"  {col.name:25s} | {nullable:12s} | {has_default}")

print()
print("=== STEP 2: Attempt Test Insert ===")
print("=" * 60)

pid = "ISDIN-FUSION-WATER-MAGIC-50"
max_id = db.query(Evidence).filter(Evidence.product_id == pid).count()
claim_id = f"EV-{pid}-{max_id + 1}"
print(f"Target claim_id: {claim_id}")

try:
    ev = Evidence(
        claim_id=claim_id,
        product_id=pid,
        claim="DEBUG TEST RECORD - safe to delete",
        field="ingredients",
        claim_type="FACT",
        source_reference="https://debug.test/qwen",
        source_type="REPUTABLE_RETAILER",
        source_date="2026-08-18",
        evidence_date=datetime.now(),
        evidence_strength="MODERATE",
        market_region="Global",
        notes="DEBUG - will be removed",
        qa_status="VERIFIED"
    )
    db.add(ev)
    db.flush()
    print("FLUSH OK — no constraint error")
    db.rollback()
    print("ROLLED BACK (test only, nothing saved)")
    print()
    print("RESULT: Model accepts these fields.")
    print("        Problem is elsewhere in import_v2.py logic.")
except Exception as e:
    db.rollback()
    print(f"FAILED: {type(e).__name__}")
    print(f"ERROR: {str(e)}")
    print()
    print("ACTION: Fix required fields based on error above.")

db.close()
