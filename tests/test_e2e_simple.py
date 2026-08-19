from sqlalchemy.engine import Engine
from sqlalchemy import event
"""
e2e.py — Simple E2E Test v2 (READ-ONLY)
Customer -> Case -> Product -> Recommendation
Fixes: Case uses reasoning_status (not status)
"""
import sys
from pathlib import Path
from datetime import datetime

PROJECT = Path("E:/HBI")
sys.path.insert(0, str(PROJECT))

results = []

def log(step, status, detail=""):
    results.append((step, status, detail))
    tag = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "INFO")
    print("  [" + tag + "] " + step + (" | " + detail if detail else ""))

print("=" * 60)
print("HBI SIMPLE E2E TEST v2 (READ-ONLY, in-memory DB)")
print("=" * 60)

# === STEP 1: Create in-memory DB ===
print("\n[STEP 1] Create in-memory database")
try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    from app.models.base import Base

    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    log("Create in-memory DB + tables", "PASS")
except Exception as e:
    log("Create in-memory DB + tables", "FAIL", str(e)[:200])
    sys.exit(1)

# === STEP 2: Create Customer ===
print("\n[STEP 2] Create Customer")
try:
    from app.services.customer_service import CustomerService
    cust_svc = CustomerService(session)
    customer = cust_svc.register_customer(
        name="E2E Test Customer",
        mobile="09120000001",
        consent_to_store_data=1
    )
    log("register_customer", "PASS",
        "id=" + str(customer.customer_id) + ", consent=" + str(customer.consent_to_store_data))
except Exception as e:
    log("register_customer", "FAIL", str(e)[:200])

# === STEP 3: Create Case (FIXED: reasoning_status) ===
print("\n[STEP 3] Create Case")
try:
    from app.models.case import Case
    case = Case(
        case_id="CASE_E2E_001",
        customer_id=customer.customer_id,
        case_type="CONSULTATION",
        reasoning_status="OPEN"
    )
    session.add(case)
    session.commit()
    log("Create Case", "PASS", "case_id=CASE_E2E_001, reasoning_status=OPEN")
except Exception as e:
    log("Create Case", "FAIL", str(e)[:200])
    session.rollback()

# === STEP 4: Create Product ===
print("\n[STEP 4] Create Product")
try:
    from app.models.product import Product
    product = Product(
        product_id="ISDIN-A-50",
        brand="ISDIN",
        product_name="Test Sunscreen SPF50",
        identity_status="VERIFIED",
        qa_verdict="VALID"
    )
    session.add(product)
    session.commit()
    log("Create Product", "PASS", "product_id=ISDIN-A-50, identity=VERIFIED")
except Exception as e:
    log("Create Product", "FAIL", str(e)[:200])
    session.rollback()

# === STEP 5: Create Inventory ===
print("\n[STEP 5] Create Inventory")
try:
    from app.models.inventory import Inventory
    inv = Inventory(
        inventory_id="INV_E2E_001",
        product_id=product.product_id,
        quantity_available=10,
        stock_status="AVAILABLE",
        sale_price_toman=850000
    )
    session.add(inv)
    session.commit()
    log("Create Inventory", "PASS", "qty=10, price=850000")
except Exception as e:
    log("Create Inventory", "FAIL", str(e)[:200])
    session.rollback()

# === STEP 6: Create ProductKnowledge ===
print("\n[STEP 6] Create ProductKnowledge")
try:
    from app.models.product_knowledge import ProductKnowledge
    pk = ProductKnowledge(
        product_knowledge_id="PK_E2E_001",
        product_id=product.product_id,
        known_use_cases="sun_protection, daily_care",
        claimed_benefits="SPF50 protection"
    )
    session.add(pk)
    session.commit()
    log("Create ProductKnowledge", "PASS")
except Exception as e:
    log("Create ProductKnowledge", "FAIL", str(e)[:200])
    session.rollback()

# === STEP 7: Create Evidence ===
print("\n[STEP 7] Create Evidence")
try:
    from app.models.evidence import Evidence
    ev = Evidence(
        evidence_id="EV_E2E_001",
        product_id=product.product_id,
        source_type="REGULATORY",
        source_reference="FDA-2026-TEST",
        claim="SPF50 verified",
        claim_type="EVIDENCE_SUPPORTED",
        evidence_status="SUPPORTED"
    )
    session.add(ev)
    session.commit()
    log("Create Evidence", "PASS", "source_type=REGULATORY")
except Exception as e:
    log("Create Evidence", "FAIL", str(e)[:200])
    session.rollback()

# === STEP 8: Query via Services ===
print("\n[STEP 8] Query via Services")
try:
    from app.services.product_service import ProductService
    prod_svc = ProductService(session)
    found = prod_svc.get_all()
    log("ProductService.get_all", "PASS", "count=" + str(len(found)))
except Exception as e:
    log("Query via Services", "FAIL", str(e)[:200])

# === STEP 9: RecommendationService ===
print("\n[STEP 9] RecommendationService")
try:
    from app.services.recommendation_service import RecommendationService
    rec_svc = RecommendationService(session)
    log("RecommendationService instantiated", "PASS")

    profile = {"concerns": "sun_protection", "skin_profile": "normal"}
    recs = rec_svc.generate_recommendations("CASE_E2E_001", profile)
    log("generate_recommendations", "PASS", "count=" + str(len(recs)))

    if recs:
        r = recs[0]
        log("Recommendation detail", "INFO",
            "id=" + str(r.recommendation_id) +
            " | need_match=" + str(r.need_match_score) +
            " | eligibility=" + str(r.eligibility_status))
except Exception as e:
    log("RecommendationService", "FAIL", str(e)[:300])

# === STEP 10: Verify _calculate_match_score value ===
print("\n[STEP 10] Verify _calculate_match_score (placeholder check)")
try:
    score = rec_svc._calculate_match_score(product, profile)
    log("_calculate_match_score", "INFO", "returned: " + str(score))
    if score == 0.75:
        log("Placeholder confirmation", "INFO", "CONFIRMED: still returns fixed 0.75")
except Exception as e:
    log("_calculate_match_score", "FAIL", str(e)[:200])

# === CLEANUP ===
session.rollback()
engine.dispose()

# === SUMMARY ===
print("\n" + "=" * 60)
print("E2E SUMMARY")
print("=" * 60)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
info = sum(1 for _, s, _ in results if s == "INFO")
print("Total: " + str(len(results)) + " | PASS: " + str(passed) + " | FAIL: " + str(failed) + " | INFO: " + str(info))
if failed == 0:
    print("RESULT: E2E PATH IS FUNCTIONAL")
else:
    print("RESULT: E2E PATH HAS FAILURES")
print("=" * 60)
print("NO PROJECT FILES WERE MODIFIED")
print("=" * 60)
