from __future__ import annotations
import argparse, logging, shutil, sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "hbi.db"
MIGRATION_SQL = ROOT / "scripts" / "schema_v1.2_migration.sql"
ROLLBACK_SQL = ROOT / "scripts" / "schema_v1.2_rollback.sql"
BACKUP_DIR = ROOT / "data" / "backups"
TARGET_VERSION = 120

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("hbi-schema-v1.2")

def get_user_version(conn): return int(conn.execute("PRAGMA user_version").fetchone()[0])
def table_exists(conn, name): return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None
def get_columns(conn, name): return {r[1] for r in conn.execute(f"PRAGMA table_info({name})").fetchall()}

def backup_database():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = BACKUP_DIR / f"hbi_before_v1_2_{ts}.db"
    shutil.copy2(DB_PATH, path)
    logger.info("Backup created: %s", path)
    return path

def verify_post(conn, expected_count):
    if get_user_version(conn) != TARGET_VERSION: raise RuntimeError("Version mismatch")
    if not table_exists(conn, "Evidence"): raise RuntimeError("Table missing")
    req = {"evidence_id","product_id","claim_id","source_type","source_reference","claim","field","market_region","notes","claim_type","evidence_strength","evidence_status","conflict_status","source_date","evidence_date","qa_status","created_at"}
    miss = req - get_columns(conn, "Evidence")
    if miss: raise RuntimeError(f"Missing columns: {miss}")
    legacy = {"evidence_level","retrieved_at"} & get_columns(conn, "Evidence")
    if legacy: raise RuntimeError(f"Legacy columns present: {legacy}")
    actual = conn.execute("SELECT COUNT(*) FROM Evidence").fetchone()[0]
    if actual != expected_count: raise RuntimeError(f"Count changed: {expected_count} -> {actual}")
    dup = conn.execute("SELECT COUNT(*) FROM (SELECT claim_id FROM Evidence WHERE claim_id IS NOT NULL GROUP BY claim_id HAVING COUNT(*)>1)").fetchone()[0]
    if dup: raise RuntimeError("Duplicate claim_ids")
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk: raise RuntimeError(f"FK violations: {fk}")
    logger.info("Post-migration verification PASSED")

def run_migration():
    if not DB_PATH.exists(): raise FileNotFoundError(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
conn.execute('PRAGMA foreign_keys=ON')
        conn.execute("PRAGMA foreign_keys = ON")
        ver = get_user_version(conn)
        logger.info("Current schema version: %s", ver)
        if ver == TARGET_VERSION: logger.info("Already v1.2. Skipped."); return
        if ver not in (0, 110): raise RuntimeError(f"Expected 110, got {ver}")
        before = conn.execute("SELECT COUNT(*) FROM Evidence").fetchone()[0]
        logger.info("Records before: %s", before)
        backup = backup_database()
        try:
            conn.executescript(MIGRATION_SQL.read_text(encoding="utf-8"))
            conn.execute("PRAGMA foreign_keys = ON")
            verify_post(conn, before)
            logger.info("CR-002 migration SUCCESS.")
        except Exception:
            logger.exception("Failed. Restoring...")
            conn.close()
            shutil.copy2(backup, DB_PATH)
            raise

def run_rollback():
    with sqlite3.connect(DB_PATH) as conn:
conn.execute('PRAGMA foreign_keys=ON')
        conn.execute("PRAGMA foreign_keys = OFF")
        if get_user_version(conn) != TARGET_VERSION: raise RuntimeError("Not v1.2")
        backup = backup_database()
        try:
            conn.executescript(ROLLBACK_SQL.read_text(encoding="utf-8"))
            logger.info("Rollback SUCCESS.")
        except Exception:
            logger.exception("Rollback failed. Restoring...")
            conn.close()
            shutil.copy2(backup, DB_PATH)
            raise

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rollback", action="store_true")
    args = p.parse_args()
    run_rollback() if args.rollback else run_migration()
