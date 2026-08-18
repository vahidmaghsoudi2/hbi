from app.database import SessionLocal
from app.models.evidence import Evidence
from sqlalchemy import inspect
from datetime import datetime
import traceback

db = SessionLocal()
rpt = []
def log(s=""):
    rpt.append(str(s))

log("========== EVIDENCE MODEL SCHEMA ==========")
mapper = inspect(Evidence)
pk = [c.name for c in mapper.primary_key]
log("PRIMARY_KEY: " + ", ".join(pk))
log("")
log("COLUMNS:")
for c in mapper.columns:
    log(f"  name={c.name} | type={c.type} | nullable={c.nullable} | pk={c.primary_key} | default={'YES' if c.default is not None else 'no'}")

log("")
log("========== ATTEMPT TEST INSERT ==========")
pid = "ISDIN-FUSION-WATER-MAGIC-50"
try:
    ev = Evidence(
        claim_id=f"EV-{pid}-999",
        product_id=pid,
        claim="DEBUG TEST - safe to delete",
        field="ingredients",
        claim_type="FACT",
        source_reference="https://debug.test/qwen",
        source_type="REPUTABLE_RETAILER",
        source_date="2026-08-18",
        evidence_date=datetime.now(),
        evidence_strength="MODERATE",
        market_region="Global",
        notes="DEBUG",
        qa_status="VERIFIED",
    )
    db.add(ev)
    db.flush()
    db.rollback()
    log("INSERT_RESULT: OK")
except Exception as e:
    db.rollback()
    log("INSERT_RESULT: FAILED")
    log("ERROR_TYPE: " + type(e).__name__)
    log("ERROR_MSG: " + str(e))
    log("")
    log("FULL_TRACEBACK:")
    log(traceback.format_exc())

db.close()

with open("debug_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rpt))

print("Full report saved to: debug_report.txt")
print("")
print("========== SHORT CONCLUSION (read this) ==========")
print("PRIMARY_KEY: " + ", ".join(pk))
for line in rpt:
    if line.startswith("INSERT_RESULT") or line.startswith("ERROR_TYPE") or line.startswith("ERROR_MSG"):
        print(line)
