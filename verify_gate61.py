"""verify_gate61.py - Verify GATE 6-1 in ONE shot"""
import sys, subprocess
from pathlib import Path

P = Path("E:/HBI")
sys.path.insert(0, str(P))

results = []

# CHECK 1: Customer.name NOT NULL DEFAULT ''
try:
    from app.models.customer import Customer
    c = Customer(customer_id='T1', mobile='09120000000', consent_to_store_data=1)
    name_val = c.name if hasattr(c, 'name') else None
    if name_val == '':
        results.append(("CHECK 1: Customer.name default", "PASS", "name=''"))
    else:
        results.append(("CHECK 1: Customer.name default", "FAIL", "name=" + repr(name_val)))
except Exception as e:
    results.append(("CHECK 1: Customer.name default", "FAIL", str(e)))

# CHECK 2: PRAGMA foreign_keys=ON
try:
    from app.database import engine
    from sqlalchemy import text
    conn = engine.connect()
    r = conn.execute(text('PRAGMA foreign_keys'))
    fk_val = r.fetchone()[0]
    conn.close()
    if fk_val == 1:
        results.append(("CHECK 2: PRAGMA foreign_keys", "PASS", "foreign_keys=1"))
    else:
        results.append(("CHECK 2: PRAGMA foreign_keys", "FAIL", "foreign_keys=" + str(fk_val)))
except Exception as e:
    results.append(("CHECK 2: PRAGMA foreign_keys", "FAIL", str(e)))

# CHECK 3: Model imports (NameError check)
try:
    from app.models.product import Product
    from app.models.customer import Customer
    from app.models.recommendation import Recommendation
    from app.models.sale import Sale
    from app.models.evidence import Evidence
    from app.models.inventory import Inventory
    results.append(("CHECK 3: Model imports", "PASS", "All imports OK"))
except Exception as e:
    results.append(("CHECK 3: Model imports", "FAIL", str(e)))

# CHECK 4: CHECK constraints inventory
try:
    from app.database import engine
    from sqlalchemy import text
    conn = engine.connect()
    r = conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql LIKE '%CHECK%'"))
    rows = r.fetchall()
    conn.close()
    detail = str(len(rows)) + " tables with CHECK"
    for row in rows:
        detail += " | " + row[0]
    results.append(("CHECK 4: CHECK constraints", "INFO", detail))
except Exception as e:
    results.append(("CHECK 4: CHECK constraints", "FAIL", str(e)))

# Build report
report = []
report.append("GATE 6-1 VERIFICATION REPORT")
report.append("Date: 2026-08-17")
report.append("=" * 60)
for name, status, detail in results:
    report.append("[" + status + "] " + name)
    report.append("        " + detail)
    report.append("")

all_pass = all(s in ("PASS", "INFO") for _, s, _ in results)
report.append("=" * 60)
if all_pass:
    report.append("VERDICT: ALL CHECKS PASSED")
    report.append("ACTION: GATE 6-1 -> APPROVED")
else:
    report.append("VERDICT: SOME CHECKS FAILED")
    report.append("ACTION: DeepSeek must fix before Phase 2")

# Save report
report_path = P / "gate61_report.txt"
report_path.write_text("\n".join(report), encoding="utf-8")

# Print
for line in report:
    print(line)

print()
print("Report saved: gate61_report.txt")

# If all pass, update Handover + commit
if all_pass:
    handover = P / "HBI_Handover.txt"
    if handover.exists():
        txt = handover.read_text(encoding="utf-8")
        old = "GATE 6-1 (Models): NOT APPROVED (DeepSeek fixing)"
        new = "GATE 6-1 (Models): APPROVED (verified by automated check, 2026-08-17)"
        if old in txt:
            txt = txt.replace(old, new, 1)
            handover.write_text(txt, encoding="utf-8")
            print("[OK] Handover updated: GATE 6-1 -> APPROVED")
        else:
            print("[SKIP] Handover pattern not found")
    
    subprocess.run(["git", "add", "-A"], cwd=str(P))
    r = subprocess.run(
        ["git", "commit", "-m", "docs: GATE 6-1 APPROVED - automated verification"],
        capture_output=True, text=True, cwd=str(P)
    )
    if r.returncode == 0:
        print("[OK] Committed")
    else:
        print("[INFO] Nothing to commit")
else:
    print()
    print("[NEXT] Send gate61_report.txt content to Qwen")