from sqlalchemy.engine import Engine
from sqlalchemy import event
"""e2e_real.py — E2E Test on REAL data/hbi.db"""
import sys
from pathlib import Path
from datetime import datetime

P = Path("E:/HBI")
sys.path.insert(0, str(P))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.customer import Customer
from app.models.case import Case
from app.models.recommendation import Recommendation
from app.services.customer_service import CustomerService
from app.services.recommendation_service import RecommendationService

print("=" * 55)
print("E2E TEST ON REAL DATABASE (data/hbi.db)")
print("=" * 55)

# Connect to REAL DB with FK enabled
engine = create_engine("sqlite:///" + str(P / "data" / "hbi.db"))
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@event.listens_for(engine, "connect")
def set_fk(dbapi_conn, conn_record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()

session = sessionmaker(bind=engine)()
results = []

def log(step, status, detail=""):
    results.append((step, status))
    tag = "PASS" if status == "PASS" else "FAIL"
    print("  [" + tag + "] " + step + (" | " + detail if detail else ""))

# ===== STEP 1: Create Customer =====
print("\n[STEP 1] Create Customer")
try:
    cust_svc = CustomerService(session)
    customer = cust_svc.register_customer(
        name="E2E Real Test Customer",
        mobile="09129999999",
        consent_to_store_data=1
    )
    log("Create Customer", "PASS", "id=" + str(customer.customer_id))
except Exception as e:
    log("Create Customer", "FAIL", str(e)[:200])
    session.rollback(); sys.exit(1)

# ===== STEP 2: Create Case =====
print("\n[STEP 2] Create Case")
try:
    case = Case(
        case_id="CASE_REAL_E2E_001",
        customer_id=customer.customer_id,
        case_type="CONSULTATION",
        reasoning_status="OPEN"
    )
    session.add(case)
    session.commit()
    log("Create Case", "PASS", "case_id=CASE_REAL_E2E_001")
except Exception as e:
    log("Create Case", "FAIL", str(e)[:200])
    session.rollback(); sys.exit(1)

# ===== STEP 3: Generate Recommendations =====
print("\n[STEP 3] Generate Recommendations")
try:
    rec_svc = RecommendationService(session)
    profile = {"concerns": "daily facial sun protection, oily-skin oil-control"}
    recs = rec_svc.generate_recommendations("CASE_REAL_E2E_001", profile)
    log("generate_recommendations", "PASS", "count=" + str(len(recs)))
    session.commit()
except Exception as e:
    log("generate_recommendations", "FAIL", str(e)[:300])
    session.rollback(); sys.exit(1)

# ===== STEP 4: Show Recommendation Details =====
print("\n[STEP 4] Recommendation Details")
for i, r in enumerate(recs, 1):
    print("  --- Recommendation " + str(i) + " ---")
    print("  product_id:       " + str(r.product_id))
    print("  need_match_score: " + str(r.need_match_score))
    print("  evidence_score:   " + str(r.evidence_score))
    print("  eligibility:      " + str(r.eligibility_status))
    print("  ranking_score:    " + str(r.ranking_score))
    print("  reasons:          " + str(r.ranking_reasons)[:100])

# ===== STEP 5: Verify Persistence =====
print("\n[STEP 5] Verify Persistence in DB")
try:
    db_recs = session.query(Recommendation).filter_by(
        case_id="CASE_REAL_E2E_001").all()
    log("Query Recommendations from DB", "PASS",
        "count=" + str(len(db_recs)))
    if len(db_recs) == len(recs):
        log("Persistence verified", "PASS",
            "DB count matches generated count")
    else:
        log("Persistence verified", "FAIL",
            "DB=" + str(len(db_recs)) + " vs Generated=" + str(len(recs)))
except Exception as e:
    log("Query Recommendations from DB", "FAIL", str(e)[:200])

# ===== STEP 6: Cleanup Test Data =====
print("\n[STEP 6] Cleanup Test Data")
try:
    session.query(Recommendation).filter_by(case_id="CASE_REAL_E2E_001").delete()
    session.query(Case).filter_by(case_id="CASE_REAL_E2E_001").delete()
    session.query(Customer).filter_by(customer_id=customer.customer_id).delete()
    session.commit()
    log("Cleanup test data", "PASS", "Customer, Case, Recommendations removed")
except Exception as e:
    log("Cleanup test data", "FAIL", str(e)[:200])
    session.rollback()

# ===== SUMMARY =====
print("\n" + "=" * 55)
print("E2E SUMMARY")
print("=" * 55)
passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
print("Total: " + str(len(results)) + " | PASS: " + str(passed) + " | FAIL: " + str(failed))
if failed == 0:
    print("RESULT: E2E ON REAL DB IS FUNCTIONAL")
else:
    print("RESULT: E2E ON REAL DB HAS FAILURES")
print("=" * 55)

session.close()
engine.dispose()