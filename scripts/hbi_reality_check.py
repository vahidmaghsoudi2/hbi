from sqlalchemy.engine import Engine
from sqlalchemy import event
"""
HBI Reality Check v0.1
EXECUTE -> OBSERVE -> REPORT (NOT MODIFY)
READ-ONLY relative to all existing project files.
Only new artifact: docs/09_gate_reports/GATE_REALITY_CHECK.md
"""
import os
import sys
import re
import ast
import sqlite3
import subprocess
import importlib
import inspect
from pathlib import Path
from datetime import datetime

PROJECT = Path("E:/HBI")
REPORT_PATH = PROJECT / "docs" / "09_gate_reports" / "GATE_REALITY_CHECK.md"
DB_PATH = PROJECT / "data" / "hbi.db"
DRY_RUN = "--dry-run" in sys.argv

results = []


def log(check_id, item, status, evidence=""):
    results.append({"check": check_id, "item": item, "status": status, "evidence": evidence})
    ev_display = (" | " + evidence[:120]) if evidence else ""
    print("  [" + status + "] " + item + ev_display)


def check_1_import():
    print("\n[CHECK 1] Import Chain Test")
    modules = ["app", "app.models", "app.repositories", "app.services", "app.interface"]
    sys.path.insert(0, str(PROJECT))
    for mod in modules:
        try:
            importlib.import_module(mod)
            log("1", "import " + mod, "PASS")
        except Exception as e:
            log("1", "import " + mod, "FAIL", str(e)[:200])


def check_2_pytest():
    print("\n[CHECK 2] Pytest Execution")
    if DRY_RUN:
        log("2", "pytest tests/", "SKIPPED", "dry-run mode")
        return
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT)
        )
        output = result.stdout + result.stderr
        summary_match = re.search(r"=+ (.+?) =+", output.split("\n")[-3] if output else "")
        summary = summary_match.group(1) if summary_match else output[-200:]
        status = "PASS" if result.returncode == 0 else "FAIL"
        log("2", "pytest tests/", status, summary[:200])
    except subprocess.TimeoutExpired:
        log("2", "pytest tests/", "FAIL", "TIMEOUT 120s")
    except Exception as e:
        log("2", "pytest tests/", "FAIL", str(e)[:200])


def check_3_connectivity():
    print("\n[CHECK 3] Layer Connectivity (in-memory DB)")
    if DRY_RUN:
        log("3", "Model->Repo->Service", "SKIPPED", "dry-run mode")
        return
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
    except ImportError as e:
        log("3", "SQLAlchemy", "NOT_VERIFIED", "not installed: " + str(e)[:100])
        return

    try:
        engine = create_engine("sqlite:///:memory:")
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
        try:
            from app.models.base import Base
            Base.metadata.create_all(engine)
            log("3", "Create tables from metadata", "PASS")
        except Exception as e:
            log("3", "Create tables from metadata", "FAIL", str(e)[:200])
            engine.dispose()
            return

        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            from app.models.customer import Customer
            from app.repositories.customer_repository import CustomerRepository
            c = Customer(name="RealityCheck", mobile="09000000001", consent=True)
            session.add(c)
            session.commit()
            repo = CustomerRepository(session)
            if hasattr(repo, "get_by_id"):
                found = repo.get_by_id(c.id)
                if found:
                    log("3", "Model->Repository (Customer)", "PASS")
                else:
                    log("3", "Model->Repository (Customer)", "FAIL", "returned None")
            else:
                methods = [m for m in dir(repo) if not m.startswith("_")]
                log("3", "Model->Repository (Customer)", "NOT_VERIFIED", "get_by_id missing, has: " + str(methods[:5]))
        except Exception as e:
            log("3", "Model->Repository (Customer)", "FAIL", str(e)[:200])

        try:
            from app.services.customer_service import CustomerService
            svc = CustomerService(session)
            log("3", "Service instantiation (CustomerService)", "PASS")
        except Exception as e:
            log("3", "Service instantiation (CustomerService)", "FAIL", str(e)[:200])

        session.rollback()
        engine.dispose()
    except Exception as e:
        log("3", "Layer connectivity", "FAIL", str(e)[:200])


def check_4_match_score():
    print("\n[CHECK 4] _calculate_match_score() Actual Value")
    if DRY_RUN:
        log("4", "_calculate_match_score", "SKIPPED", "dry-run mode")
        return
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        from app.services.recommendation_service import RecommendationService
        svc = RecommendationService(session)

        if not hasattr(svc, "_calculate_match_score"):
            log("4", "_calculate_match_score", "FAIL", "method not found")
            session.rollback()
            engine.dispose()
            return

        sig = inspect.signature(svc._calculate_match_score)
        params = list(sig.parameters.keys())
        log("4", "method signature", "INFO", "params: " + str(params))

        try:
            if len(params) <= 1:
                result = svc._calculate_match_score()
                log("4", "_calculate_match_score()", "PASS",
                    "returned: " + str(result) + " (type: " + type(result).__name__ + ")")
            else:
                log("4", "_calculate_match_score()", "NOT_VERIFIED",
                    "requires args: " + str(params[1:]))
        except Exception as e:
            log("4", "_calculate_match_score()", "FAIL", str(e)[:200])

        session.rollback()
        engine.dispose()
    except ImportError as e:
        log("4", "_calculate_match_score", "NOT_VERIFIED", "import error: " + str(e)[:100])
    except Exception as e:
        log("4", "_calculate_match_score", "FAIL", str(e)[:200])


def check_5_stubs():
    print("\n[CHECK 5] Stub/Placeholder Detection")
    services_dir = PROJECT / "app" / "services"
    if not services_dir.exists():
        log("5", "services directory", "FAIL", "not found")
        return

    stubs_found = 0
    for py_file in sorted(services_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return) and child.value:
                            if isinstance(child.value, ast.Constant):
                                stubs_found += 1
                                log("5", py_file.name + "::" + node.name, "STUB",
                                    "returns constant: " + repr(child.value.value))
                    body = [n for n in node.body if not isinstance(n, ast.Expr)]
                    if len(body) == 1 and isinstance(body[0], ast.Pass):
                        stubs_found += 1
                        log("5", py_file.name + "::" + node.name, "STUB", "body is only pass")
                    for child in ast.walk(node):
                        if isinstance(child, ast.Raise) and child.exc:
                            if isinstance(child.exc, ast.Call) and hasattr(child.exc.func, "id"):
                                if child.exc.func.id == "NotImplementedError":
                                    stubs_found += 1
                                    log("5", py_file.name + "::" + node.name, "STUB",
                                        "raises NotImplementedError")
            upper_src = source.upper()
            if "TODO" in upper_src or "FIXME" in upper_src or "PLACEHOLDER" in upper_src:
                log("5", py_file.name, "NOTE", "contains TODO/FIXME/PLACEHOLDER")
        except SyntaxError:
            log("5", py_file.name, "FAIL", "SYNTAX ERROR in file")

    if stubs_found == 0:
        log("5", "No stubs detected in services", "PASS")
    else:
        log("5", "Total stubs/placeholders", "INFO", str(stubs_found) + " found")


def check_6_e2e():
    print("\n[CHECK 6] End-to-End Path (Customer -> Case -> Recommendation)")
    if DRY_RUN:
        log("6", "E2E path", "SKIPPED", "dry-run mode")
        return
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            from app.models.customer import Customer
            customer = Customer(name="E2E Test", mobile="09111111111", consent=True)
            session.add(customer)
            session.commit()
            log("6", "Step 1: Create Customer", "PASS", "id=" + str(customer.id))
        except Exception as e:
            log("6", "Step 1: Create Customer", "FAIL", str(e)[:200])
            session.rollback()
            engine.dispose()
            return

        try:
            from app.models.case import Case
            case = Case(customer_id=customer.id)
            session.add(case)
            session.commit()
            log("6", "Step 2: Create Case", "PASS", "id=" + str(case.id))
        except Exception as e:
            log("6", "Step 2: Create Case", "FAIL", str(e)[:200])
            session.rollback()
            engine.dispose()
            return

        try:
            from app.services.recommendation_service import RecommendationService
            svc = RecommendationService(session)
            log("6", "Step 3: RecommendationService instantiated", "PASS")
            if hasattr(svc, "generate_recommendations"):
                try:
                    recs = svc.generate_recommendations(case.id)
                    count = len(recs) if recs else 0
                    log("6", "Step 3: generate_recommendations", "PASS", "count=" + str(count))
                except Exception as e:
                    log("6", "Step 3: generate_recommendations", "FAIL", str(e)[:200])
            elif hasattr(svc, "generate"):
                try:
                    recs = svc.generate(case.id)
                    count = len(recs) if recs else 0
                    log("6", "Step 3: generate", "PASS", "count=" + str(count))
                except Exception as e:
                    log("6", "Step 3: generate", "FAIL", str(e)[:200])
            else:
                methods = [m for m in dir(svc) if not m.startswith("_")]
                log("6", "Step 3: recommendation method", "NOT_VERIFIED",
                    "available methods: " + str(methods[:6]))
        except Exception as e:
            log("6", "Step 3: RecommendationService", "FAIL", str(e)[:200])

        session.rollback()
        engine.dispose()
    except ImportError as e:
        log("6", "E2E path", "NOT_VERIFIED", "import error: " + str(e)[:100])
    except Exception as e:
        log("6", "E2E path", "FAIL", str(e)[:200])


def check_7_legacy():
    print("\n[CHECK 7] Legacy Scripts Safety Check")
    legacy_scripts = [
        PROJECT / "scripts" / "hbi_check.py",
        PROJECT / "scripts" / "hbi_gate64_preflight.py",
    ]
    write_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE TABLE", ".COMMIT(", ".WRITE("]

    for script in legacy_scripts:
        if not script.exists():
            log("7", script.name, "NOT_FOUND")
            continue
        if DRY_RUN:
            log("7", script.name, "SKIPPED", "dry-run mode")
            continue
        try:
            content = script.read_text(encoding="utf-8", errors="replace").upper()
            has_write = any(kw in content for kw in write_keywords)
            if has_write:
                log("7", script.name, "NOT_EXECUTED", "contains write operations - safety block")
                continue
        except Exception as e:
            log("7", script.name, "FAIL", "cannot read: " + str(e)[:100])
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=60, cwd=str(PROJECT)
            )
            status = "PASS" if result.returncode == 0 else "FAIL"
            preview = (result.stdout + result.stderr)[:200].replace("\n", " ")
            log("7", script.name, status, preview)
        except subprocess.TimeoutExpired:
            log("7", script.name, "FAIL", "TIMEOUT 60s")
        except Exception as e:
            log("7", script.name, "FAIL", str(e)[:200])


def check_8_database():
    print("\n[CHECK 8] Database Inspection (READ-ONLY)")
    if not DB_PATH.exists():
        log("8", "hbi.db", "FAIL", "file not found at data/hbi.db")
        return
    try:
        uri = "file:" + str(DB_PATH).replace("\\", "/") + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        log("8", "Tables found", "PASS" if tables else "FAIL",
            str(len(tables)) + " tables: " + ", ".join(tables[:10]))

        for table in tables:
            try:
                cursor.execute('SELECT COUNT(*) FROM "' + table + '"')
                count = cursor.fetchone()[0]
                log("8", "Table '" + table + "' row count", "INFO", str(count))
            except Exception as e:
                log("8", "Table '" + table + "' row count", "FAIL", str(e)[:100])

        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        log("8", "PRAGMA foreign_keys", "INFO", "value=" + str(fk_status))

        conn.close()
    except Exception as e:
        log("8", "Database connection", "FAIL", str(e)[:200])


def generate_report():
    print("\n[REPORT] Generating GATE_REALITY_CHECK.md")
    lines = []
    lines.append("# HBI REALITY CHECK REPORT")
    lines.append("> Evidence Artifact - Generated by hbi_reality_check.py")
    lines.append("> Principle: EXECUTE -> OBSERVE -> REPORT")
    lines.append("> Mode: " + ("DRY-RUN" if DRY_RUN else "FULL EXECUTION"))
    lines.append("")
    lines.append("## META")
    lines.append("| Key | Value |")
    lines.append("|---|---|")
    lines.append("| generated_at | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " |")
    lines.append("| python_version | " + sys.version.split()[0] + " |")
    lines.append("| project_root | E:/HBI |")
    lines.append("| mode | " + ("DRY-RUN" if DRY_RUN else "FULL") + " |")
    lines.append("")
    lines.append("## CHECK RESULTS")
    lines.append("| Check | Item | Status | Evidence |")
    lines.append("|---|---|---|---|")
    for r in results:
        ev = r["evidence"].replace("|", "/").replace("\n", " ")[:150] if r["evidence"] else ""
        lines.append("| " + r["check"] + " | " + r["item"] + " | " + r["status"] + " | " + ev + " |")
    lines.append("")
    lines.append("## SUMMARY")
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    not_verified = sum(1 for r in results if r["status"] in ("NOT_VERIFIED", "NOT_EXECUTED", "NOT_FOUND"))
    stubs = sum(1 for r in results if r["status"] == "STUB")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| Total checks | " + str(total) + " |")
    lines.append("| PASS | " + str(passed) + " |")
    lines.append("| FAIL | " + str(failed) + " |")
    lines.append("| NOT_VERIFIED / NOT_EXECUTED | " + str(not_verified) + " |")
    lines.append("| STUB detected | " + str(stubs) + " |")
    lines.append("")
    lines.append("## END OF REPORT")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("[OK] Report written to: " + str(REPORT_PATH))


def main():
    print("=" * 60)
    print("HBI REALITY CHECK v0.1")
    print("Mode: " + ("DRY-RUN (structure only)" if DRY_RUN else "FULL EXECUTION"))
    print("=" * 60)

    check_1_import()
    check_2_pytest()
    check_3_connectivity()
    check_4_match_score()
    check_5_stubs()
    check_6_e2e()
    check_7_legacy()
    check_8_database()
    generate_report()

    print("\n" + "=" * 60)
    print("REALITY CHECK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()