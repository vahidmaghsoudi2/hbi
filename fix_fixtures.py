"""fix_fixtures.py — Add cleanup to db fixture"""
import re, subprocess, sys
from pathlib import Path

P = Path("E:/HBI")
TF = P / "tests" / "test_interface.py"

txt = TF.read_text(encoding="utf-8")

OLD_FIXTURE = r'@pytest\.fixture\ndef db\(\):\n    session = SessionLocal\(\)\n    try:\n        yield session\n    finally:\n        session\.rollback\(\)\n        session\.close\(\)'

NEW_FIXTURE = '''@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        # Cleanup all test data
        from app.models.recommendation import Recommendation
        from app.models.case import Case
        from app.models.sale_item import SaleItem
        from app.models.sale import Sale
        from app.models.inventory import Inventory
        from app.models.customer import Customer
        from app.models.product import Product
        
        session.query(Recommendation).filter(Recommendation.case_id.like("CASE_%")).delete(synchronize_session=False)
        session.query(Case).filter(Case.case_id.like("CASE_%")).delete(synchronize_session=False)
        session.query(SaleItem).delete(synchronize_session=False)
        session.query(Sale).delete(synchronize_session=False)
        session.query(Inventory).filter(Inventory.inventory_id.like("I%")).delete(synchronize_session=False)
        session.query(Customer).filter(Customer.customer_id.like("C%")).delete(synchronize_session=False)
        session.query(Product).filter(Product.product_id.like("P%")).delete(synchronize_session=False)
        session.commit()
        session.close()'''

m = re.search(OLD_FIXTURE, txt)
if not m:
    print("[FAIL] db fixture not found. No changes.")
    sys.exit(1)

if "Cleanup all test data" in txt:
    print("[SKIP] Already patched.")
    sys.exit(0)

new_txt = txt[:m.start()] + NEW_FIXTURE + txt[m.end():]
backup = TF.with_suffix(".py.bak2")
backup.write_text(txt, encoding="utf-8")
TF.write_text(new_txt, encoding="utf-8")
print("[OK] Patched db fixture with cleanup")
print("[OK] Backup: test_interface.py.bak2")

# Run pytest
print("\n" + "=" * 50)
print("RUNNING PYTEST...")
print("=" * 50)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    capture_output=True, text=True, cwd=str(P)
)
out = r.stdout
print(out[-2000:] if len(out) > 2000 else out)
if r.returncode == 0:
    print("\n[SUCCESS] All tests passed!")
else:
    print("\n[WARN] Some tests still failing.")
print("=" * 50)