"""HBI Control Center v2.2 - clear_screen disabled permanently"""
import sys, os, subprocess, shutil
from pathlib import Path
from datetime import datetime

P = Path("E:/HBI")
LOG = P / "hbi_log.txt"
STATUS_FILE = P / "docs" / "01_project_state" / "CURRENT_STATUS.md"
BACKUPS = P / ".backups"
BACKUPS.mkdir(exist_ok=True)

def clear_screen():
    pass  # DISABLED - output stays visible

def log(msg):
    line = "[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def backup(path):
    if path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = BACKUPS / (path.name + "." + ts + ".bak")
        shutil.copy(path, dst)
        return dst
    return None

def run_cmd(cmd, cwd=P):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    return r.returncode, r.stdout, r.stderr

def git_commit(msg):
    run_cmd(["git", "add", "-A"])
    rc, out, _ = run_cmd(["git", "commit", "-m", msg])
    if rc == 0:
        log("[OK] git commit: " + msg)
    else:
        log("[INFO] git commit: nothing to commit")

def cmd_status():
    log("=== Project Status ===")
    _, out, _ = run_cmd(["git", "status", "--short"])
    print("Git Status:")
    print(out if out.strip() else "  (clean)")
    print()
    _, out, _ = run_cmd(["git", "log", "--oneline", "-5"])
    print("Last 5 commits:")
    print(out)
    try:
        sys.path.insert(0, str(P))
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.product import Product
        from app.models.evidence import Evidence
        from app.models.inventory import Inventory
        engine = create_engine("sqlite:///" + str(P / "data" / "hbi.db"))
        s = sessionmaker(bind=engine)()
        print("DB Counts:")
        print("  Products: " + str(s.query(Product).count()))
        print("  Evidence: " + str(s.query(Evidence).count()))
        print("  Inventory: " + str(s.query(Inventory).count()))
        s.close(); engine.dispose()
    except Exception as e:
        print("  [WARN] Cannot read DB: " + str(e))

def cmd_pytest():
    log("=== Running pytest ===")
    os.environ["PYTHONPATH"] = str(P)
    rc, out, err = run_cmd([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
    print(out[-2000:] if len(out) > 2000 else out)
    if rc == 0:
        log("=== ALL TESTS PASSED ===")
    else:
        log("=== SOME TESTS FAILED ===")

def cmd_e2e_real():
    log("=== Running E2E on real DB ===")
    e2e = P / "tests" / "test_e2e_real.py"
    if not e2e.exists():
        log("[WARN] " + str(e2e) + " not found")
        return
    rc, out, _ = run_cmd([sys.executable, str(e2e)])
    print(out)
    log("E2E exit code: " + str(rc))

def cmd_inject_evidence():
    log("=== Injecting Evidence A & B ===")
    try:
        sys.path.insert(0, str(P))
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.product import Product
        from app.models.product_knowledge import ProductKnowledge
        from app.models.evidence import Evidence
        from app.models.inventory import Inventory
    except Exception as e:
        log("[FAIL] Import error: " + str(e))
        return
    engine = create_engine("sqlite:///" + str(P / "data" / "hbi.db"))
    session = sessionmaker(bind=engine)()
    count = 0
    if not session.query(Product).filter_by(product_id="ISDIN-FUSION-WATER-MAGIC-50").first():
        session.add(Product(product_id="ISDIN-FUSION-WATER-MAGIC-50", brand="ISDIN",
            product_name="Fusion Water MAGIC SPF 50", identity_status="VERIFIED"))
        count += 1
    if not session.query(ProductKnowledge).filter_by(product_id="ISDIN-FUSION-WATER-MAGIC-50").first():
        session.add(ProductKnowledge(product_knowledge_id="PK-A",
            product_id="ISDIN-FUSION-WATER-MAGIC-50",
            known_use_cases="daily facial sun protection, oily-skin oil-control",
            claimed_benefits="SPF50, ultralight, non-greasy"))
        count += 1
    url_a = "https://www.isdin.com/en-GB/product/fotoprotector-isdin/magic-spf-50"
    for eid, cl, ct, es in [("EV-A-001","50 ml SPF 50 product","FACT","SUPPORTED"),
                             ("EV-A-002","Ultralight daily sunscreen","MANUFACTURER_CLAIM","SUPPORTED"),
                             ("EV-A-003","SPF 50 lab tested","EVIDENCE_SUPPORTED","PARTIAL"),
                             ("EV-A-004","30 subjects study","EVIDENCE_SUPPORTED","PARTIAL")]:
        if not session.query(Evidence).filter_by(evidence_id=eid).first():
            session.add(Evidence(evidence_id=eid, product_id="ISDIN-FUSION-WATER-MAGIC-50",
                claim=cl, claim_type=ct, source_reference=url_a,
                source_type="OFFICIAL_MANUFACTURER", evidence_status=es,
                conflict_status="NONE", source_date="2026-08-14"))
            count += 1
    if not session.query(Inventory).filter_by(product_id="ISDIN-FUSION-WATER-MAGIC-50").first():
        session.add(Inventory(inventory_id="INV-A-001",
            product_id="ISDIN-FUSION-WATER-MAGIC-50", quantity_available=5,
            stock_status="AVAILABLE", sale_price_toman=2500000))
        count += 1
    if not session.query(Product).filter_by(product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").first():
        session.add(Product(product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", brand="ISDIN",
            product_name="Fotoultra 100 Active Unify COLOR SPF 50+", identity_status="VERIFIED"))
        count += 1
    if not session.query(ProductKnowledge).filter_by(product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").first():
        session.add(ProductKnowledge(product_knowledge_id="PK-B",
            product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50",
            known_use_cases="pigmentation, tinted sunscreen",
            claimed_benefits="SPF50+, tone-evening, depigmenting"))
        count += 1
    url_b = "https://www.isdin.com/en-GB/product/foto-ultra-isdin/active-unify-color-spf-50"
    for eid, cl, ct, es in [("EV-B-001","50 ml SPF 50+ product","FACT","SUPPORTED"),
                             ("EV-B-002","Triple depigmenting action","MANUFACTURER_CLAIM","SUPPORTED"),
                             ("EV-B-003","SPF 50+ UVA protection","EVIDENCE_SUPPORTED","PARTIAL"),
                             ("EV-B-004","Dermatologically tested","MANUFACTURER_CLAIM","SUPPORTED")]:
        if not session.query(Evidence).filter_by(evidence_id=eid).first():
            session.add(Evidence(evidence_id=eid, product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50",
                claim=cl, claim_type=ct, source_reference=url_b,
                source_type="OFFICIAL_MANUFACTURER", evidence_status=es,
                conflict_status="NONE", source_date="2026-08-14"))
            count += 1
    if not session.query(Inventory).filter_by(product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50").first():
        session.add(Inventory(inventory_id="INV-B-001",
            product_id="ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50", quantity_available=3,
            stock_status="AVAILABLE", sale_price_toman=3200000))
        count += 1
    session.commit()
    log("Injected " + str(count) + " records")
    session.close(); engine.dispose()
    git_commit("feat(data): inject ISDIN A&B evidence (via Control Center)")

def cmd_map_availability_price():
    log("=== Mapping availability and price ===")
    facades = P / "app" / "interface" / "facades.py"
    txt = facades.read_text(encoding="utf-8")
    old = "        evidence_refs=[],\n        warnings=[],\n        availability=None,\n        price=None,\n    )"
    new = "        evidence_refs=[],\n        warnings=[],\n        availability=_get_availability(r),\n        price=_get_price(r),\n    )"
    if old not in txt:
        log("[INFO] availability/price already mapped or pattern changed")
        log("[INFO] Current state of _to_recommendation_dto:")
        start = txt.find("def _to_recommendation_dto")
        if start != -1:
            print(txt[start:start+1000])
        return
    helpers = "\n\ndef _get_availability(r):\n    try:\n        from app.models.inventory import Inventory\n        from app.database import SessionLocal\n        s = SessionLocal()\n        inv = s.query(Inventory).filter_by(product_id=r.product_id).first()\n        s.close()\n        if not inv:\n            return \"OUT_OF_STOCK\"\n        return \"AVAILABLE\" if inv.quantity_available > 0 else \"OUT_OF_STOCK\"\n    except Exception:\n        return \"UNKNOWN\"\n\ndef _get_price(r):\n    try:\n        from app.models.inventory import Inventory\n        from app.database import SessionLocal\n        s = SessionLocal()\n        inv = s.query(Inventory).filter_by(product_id=r.product_id).first()\n        price = inv.sale_price_toman if inv else None\n        s.close()\n        return price\n    except Exception:\n        return None\n\n"
    import_end = txt.find("\ndef _to_recommendation_dto")
    if import_end == -1:
        log("[FAIL] Cannot find _to_recommendation_dto")
        return
    backup(facades)
    new_txt = txt[:import_end] + helpers + txt[import_end:]
    new_txt = new_txt.replace(old, new, 1)
    facades.write_text(new_txt, encoding="utf-8")
    log("[OK] Patched facades.py")
    git_commit("feat(contract): map availability and price in Recommendation DTO")

def cmd_save_status():
    log("=== Saving Project Status ===")
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _, git_log, _ = run_cmd(["git", "log", "--oneline", "-10"])
    _, git_status, _ = run_cmd(["git", "status", "--short"])
    db_info = ""
    try:
        sys.path.insert(0, str(P))
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.product import Product
        from app.models.evidence import Evidence
        from app.models.inventory import Inventory
        engine = create_engine("sqlite:///" + str(P / "data" / "hbi.db"))
        s = sessionmaker(bind=engine)()
        db_info = "| Table | Count |\n|---|---|\n"
        db_info += "| Products | " + str(s.query(Product).count()) + " |\n"
        db_info += "| Evidence | " + str(s.query(Evidence).count()) + " |\n"
        db_info += "| Inventory | " + str(s.query(Inventory).count()) + " |\n"
        s.close(); engine.dispose()
    except Exception as e:
        db_info = "Cannot read DB: " + str(e)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("# HBI PROJECT - CURRENT STATUS")
    lines.append("")
    lines.append("**Generated:** " + now)
    lines.append("**By:** HBI Control Center v2.2")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Project Phase")
    lines.append("")
    lines.append("**Status:** Phase 1 COMPLETE - Awaiting Phase 2")
    lines.append("")
    lines.append("## Git Log (last 10)")
    lines.append("")
    lines.append("```")
    lines.append(git_log)
    lines.append("```")
    lines.append("")
    lines.append("## Git Status")
    lines.append("")
    lines.append("```")
    lines.append(git_status if git_status.strip() else "(clean)")
    lines.append("```")
    lines.append("")
    lines.append("## Database Counts")
    lines.append("")
    lines.append(db_info)
    lines.append("")
    lines.append("## Known Deferred Items (PO Decision)")
    lines.append("")
    lines.append("| Item | Status |")
    lines.append("|---|---|")
    lines.append("| Products C & D (UNIDENTIFIED) | Deferred to next version |")
    lines.append("| barcode_gtin for A & B | Deferred to next version |")
    lines.append("")
    lines.append("## Architecture Decisions (Frozen)")
    lines.append("")
    lines.append("| ID | Decision | Status |")
    lines.append("|----|----------|--------|")
    lines.append("| AD-1 | Scoring Weights (Need 0.50, Evidence 0.30, Inventory 0.20) | FROZEN |")
    lines.append("| AD-2 | Confidence Formula (0.4*need + 0.6*evidence) + Thresholds | FROZEN |")
    lines.append("| AD-3 | Recommendation Contract (16 fields) | IMPLEMENTED |")
    lines.append("| AD-4 | Hard Gates (evidence=0 or inventory=0 -> NEEDS_REVIEW) | IMPLEMENTED |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This file is auto-generated by HBI Control Center v2.2*")
    content = "\n".join(lines)
    STATUS_FILE.write_text(content, encoding="utf-8")
    log("[OK] Status saved to " + str(STATUS_FILE.relative_to(P)))
    git_commit("docs: update CURRENT_STATUS.md (via Control Center)")

def cmd_cleanup():
    log("=== Cleanup (safe - only temp files) ===")
    for f in ["inspect_dto.py","check_scoring.py","fix_test.py","fix_fixtures.py",
              "simple_fix.py","final_fix.py","final_fix_v2.py","final_fix_v3.py",
              "upgrade_dto.py","upgrade_facade.py","diagnostic.txt","patch_no_clear.py"]:
        p = P / f
        if p.exists():
            p.unlink()
            log("[DEL] " + f)
    for f in (P / "tests").glob("*.bak*"):
        f.unlink()
        log("[DEL] " + f.name)
    git_commit("chore: cleanup temp files (via Control Center)")

def cmd_git_log():
    _, out, _ = run_cmd(["git", "log", "--oneline", "-10"])
    print(out)

def cmd_setup_small_cmd():
    log("=== Setting up small CMD ===")
    bat_lines = []
    bat_lines.append("@echo off")
    bat_lines.append("title HBI Control Center")
    bat_lines.append("mode con: cols=80 lines=25")
    bat_lines.append("cd /d E:\\HBI")
    bat_lines.append("py -3 hbi.py")
    bat_path = P / "hbi_small.bat"
    bat_path.write_text("\n".join(bat_lines), encoding="utf-8")
    log("[OK] Created " + bat_path.name)

MENU = """
+=============================================================+
|       HBI CONTROL CENTER v2.2                               |
|       (output stays visible - no clear screen)              |
+=============================================================+
|  1. Status (git + DB counts)                                |
|  2. Run pytest (all tests)                                  |
|  3. Run E2E on real DB                                      |
|  4. Inject Evidence A & B                                   |
|  5. Map availability & price (one-time patch)               |
|  6. Save Project Status to CURRENT_STATUS.md                |
|  7. Cleanup temp files                                      |
|  8. Git log (last 10)                                       |
|  9. Setup small CMD window                                  |
|  0. Exit                                                    |
+=============================================================+
"""

CMDS = {
    "1": cmd_status,
    "2": cmd_pytest,
    "3": cmd_e2e_real,
    "4": cmd_inject_evidence,
    "5": cmd_map_availability_price,
    "6": cmd_save_status,
    "7": cmd_cleanup,
    "8": cmd_git_log,
    "9": cmd_setup_small_cmd,
}

def main():
    log("=== HBI Control Center v2.2 started ===")
    while True:
        print(MENU)
        choice = input("Enter number: ").strip()
        if choice == "0":
            log("=== Exit ===")
            break
        fn = CMDS.get(choice)
        if fn:
            try:
                fn()
            except Exception as e:
                log("[ERROR] " + str(e))
        else:
            print("Invalid choice")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()