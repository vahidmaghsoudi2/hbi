"""fix_test.py — Patch test_recommendation_facade_generate"""
import re, subprocess, sys
from pathlib import Path

P = Path("E:/HBI")
TF = P / "tests" / "test_interface.py"

txt = TF.read_text(encoding="utf-8")

OLD_FUNC = r'def test_recommendation_facade_generate\(.*?\n(?=\ndef |\Z)'

NEW_FUNC = '''def test_recommendation_facade_generate(db, sample_product, sample_customer, sample_inventory):
    from app.models.product_knowledge import ProductKnowledge
    from app.models.evidence import Evidence

    # Add ProductKnowledge for scoring
    pk = ProductKnowledge(
        product_knowledge_id="PK_TEST_001",
        product_id=sample_product.product_id,
        known_use_cases="oily skin care, daily protection",
        claimed_benefits="oil control"
    )
    db.add(pk)

    # Add Evidence for scoring
    ev = Evidence(
        evidence_id="EV_TEST_001",
        product_id=sample_product.product_id,
        source_type="OFFICIAL_MANUFACTURER",
        source_reference="TEST-SOURCE",
        claim="Test claim for oily skin",
        claim_type="FACT",
        evidence_status="SUPPORTED"
    )
    db.add(ev)
    db.commit()

    case_facade = CaseFacade(db)
    case = case_facade.create(customer_id=sample_customer.customer_id)
    rec_facade = RecommendationFacade(db)
    recs = rec_facade.generate(case.case_id, {"concerns": "oily skin care"})
    assert len(recs) >= 1
    assert recs[0].case_id == case.case_id

'''

m = re.search(OLD_FUNC, txt, re.DOTALL)
if not m:
    print("[FAIL] Function not found. No changes.")
    sys.exit(1)

if "PK_TEST_001" in txt:
    print("[SKIP] Already patched.")
    sys.exit(0)

new_txt = txt[:m.start()] + NEW_FUNC + txt[m.end():]
backup = TF.with_suffix(".py.bak")
backup.write_text(txt, encoding="utf-8")
TF.write_text(new_txt, encoding="utf-8")
print("[OK] Patched test_recommendation_facade_generate")
print("[OK] Backup: test_interface.py.bak")

# Run pytest
print("\n" + "=" * 50)
print("RUNNING PYTEST...")
print("=" * 50)
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    capture_output=True, text=True, cwd=str(P)
)
out = r.stdout
# Print last 2000 chars to see summary
print(out[-2000:] if len(out) > 2000 else out)
if r.returncode == 0:
    print("\n[SUCCESS] All tests passed!")
else:
    print("\n[WARN] Some tests still failing. Check output.")
print("=" * 50)