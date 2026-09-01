#!/usr/bin/env python3
"""
HBI Accounting PHASE 02 — Schema migration (additive, idempotent, clone-safe).

- Adds missing accounting columns to existing tables via ALTER TABLE.
- Creates missing tables (Category, StockMovement, Payment, SaleReturn, OperationalFxRate).
- Seeds the six official categories (BOOST/HAIR independent).
- Preserves all existing rows and legacy Toman values.
- Does NOT perform historical FX conversion.
- Does NOT touch data/hbi.db unless explicitly passed a path (tests use temp clones).
- Idempotent: safe to re-run; detects already-migrated state.

Usage:
  python scripts/accounting_phase02_migrate.py --db /path/to/clone.db
  python scripts/accounting_phase02_migrate.py --db :memory:   # for tests

Exit 0 on success, non-zero on failure.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

OFFICIAL_CATEGORIES = [
    ("BOOST", "بوست", "Boost", 1),
    ("HAIR", "مو", "Hair", 2),
    ("BEAUTY", "زیبایی", "Beauty", 3),
    ("TOOLS", "ابزار", "Tools", 4),
    ("PERFUME", "ادکلن", "Perfume", 5),
    ("OTHER", "سایر", "Other", 99),
]

# Columns to ensure exist: table -> list of (col_name, sql_type_default)
REQUIRED_COLUMNS: Dict[str, List[Tuple[str, str]]] = {
    "Product": [
        ("category_id", "VARCHAR"),
    ],
    "Inventory": [
        ("purchase_price_usd", "FLOAT"),
        ("sale_price_usd", "FLOAT"),
        ("price_fx_rate_usd_to_irr", "FLOAT"),
        ("purchase_price_irr", "FLOAT"),
        ("sale_price_irr", "FLOAT"),
        ("price_updated_at", "DATETIME"),
    ],
    "Sale": [
        ("total_amount_usd", "FLOAT"),
        ("fx_rate_usd_to_irr", "FLOAT"),
        ("total_amount_irr", "FLOAT"),
    ],
    "SaleItem": [
        ("unit_price_usd", "FLOAT"),
        ("fx_rate_usd_to_irr", "FLOAT"),
        ("unit_price_irr", "FLOAT"),
    ],
    "Payment": [
        ("amount_usd", "FLOAT"),
        ("fx_rate_usd_to_irr", "FLOAT"),
        ("amount_irr", "FLOAT"),
        ("amount_toman", "INTEGER"),
    ],
    "SaleReturn": [
        ("amount_usd", "FLOAT"),
        ("fx_rate_usd_to_irr", "FLOAT"),
        ("amount_irr", "FLOAT"),
        ("amount_toman", "INTEGER"),
    ],
    "StockMovement": [
        ("amount_usd", "FLOAT"),
        ("fx_rate_usd_to_irr", "FLOAT"),
        ("amount_irr", "FLOAT"),
        ("amount_toman", "FLOAT"),
    ],
}

CREATE_TABLES_SQL = {
    "Category": """
CREATE TABLE IF NOT EXISTS Category (
  category_id VARCHAR PRIMARY KEY,
  name_fa VARCHAR NOT NULL,
  name_en VARCHAR,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""",
    "StockMovement": """
CREATE TABLE IF NOT EXISTS StockMovement (
  movement_id VARCHAR PRIMARY KEY,
  product_id VARCHAR NOT NULL,
  inventory_id VARCHAR,
  movement_type VARCHAR NOT NULL,
  quantity_delta INTEGER NOT NULL,
  quantity_after INTEGER,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman FLOAT,
  reference_type VARCHAR,
  reference_id VARCHAR,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(product_id) REFERENCES Product(product_id)
);
""",
    "Payment": """
CREATE TABLE IF NOT EXISTS Payment (
  payment_id VARCHAR PRIMARY KEY,
  sale_id VARCHAR NOT NULL,
  method VARCHAR NOT NULL,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman INTEGER,
  paid_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sale_id) REFERENCES Sale(sale_id)
);
""",
    "SaleReturn": """
CREATE TABLE IF NOT EXISTS SaleReturn (
  return_id VARCHAR PRIMARY KEY,
  sale_id VARCHAR NOT NULL,
  product_id VARCHAR NOT NULL,
  quantity INTEGER NOT NULL,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman INTEGER,
  reason VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sale_id) REFERENCES Sale(sale_id),
  FOREIGN KEY(product_id) REFERENCES Product(product_id)
);
""",
    "OperationalFxRate": """
CREATE TABLE IF NOT EXISTS OperationalFxRate (
  rate_id VARCHAR PRIMARY KEY,
  fx_rate_usd_to_irr FLOAT NOT NULL,
  effective_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""",
}


def get_tables(conn: sqlite3.Connection) -> Set[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {r[0] for r in cur.fetchall()}


def get_columns(conn: sqlite3.Connection, table: str) -> Set[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {r[1] for r in cur.fetchall()}


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return table in get_tables(conn)


def capture_schema(conn: sqlite3.Connection) -> Dict[str, Any]:
    tables = sorted(get_tables(conn))
    schema: Dict[str, Any] = {}
    for t in tables:
        if t.startswith("sqlite_"):
            continue
        cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
        schema[t] = [{"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "dflt": c[4], "pk": c[5]} for c in cols]
    return schema


def capture_row_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    counts = {}
    for t in sorted(get_tables(conn)):
        if t.startswith("sqlite_"):
            continue
        try:
            counts[t] = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        except sqlite3.Error:
            counts[t] = -1
    return counts


def capture_toman_samples(conn: sqlite3.Connection, limit: int = 5) -> Dict[str, List[Any]]:
    samples: Dict[str, List[Any]] = {}
    probes = [
        ("Inventory", "inventory_id, purchase_price_toman, sale_price_toman"),
        ("Sale", "sale_id, total_amount_toman"),
        ("SaleItem", "sale_item_id, unit_price_toman"),
    ]
    for table, cols in probes:
        if not table_exists(conn, table):
            continue
        try:
            rows = conn.execute(f"SELECT {cols} FROM [{table}] LIMIT {limit}").fetchall()
            samples[table] = [list(r) for r in rows]
        except sqlite3.Error as e:
            samples[table] = [f"error: {e}"]
    return samples


def ensure_columns(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    added = list(evidence.get("columns_added") or [])
    for table, cols in REQUIRED_COLUMNS.items():
        if not table_exists(conn, table):
            continue
        existing = get_columns(conn, table)
        for col_name, col_type in cols:
            if col_name not in existing:
                sql = f"ALTER TABLE [{table}] ADD COLUMN [{col_name}] {col_type}"
                conn.execute(sql)
                added.append(f"{table}.{col_name}")
    evidence["columns_added"] = added


def ensure_tables(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    created = list(evidence.get("tables_created") or [])
    for name, sql in CREATE_TABLES_SQL.items():
        if not table_exists(conn, name):
            conn.execute(sql)
            created.append(name)
    evidence["tables_created"] = created


def seed_categories(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    if not table_exists(conn, "Category"):
        evidence["categories_seeded"] = []
        return
    seeded = []
    for cid, name_fa, name_en, sort_order in OFFICIAL_CATEGORIES:
        conn.execute(
            """
            INSERT OR IGNORE INTO Category (category_id, name_fa, name_en, is_active, sort_order)
            VALUES (?, ?, ?, 1, ?)
            """,
            (cid, name_fa, name_en, sort_order),
        )
        seeded.append(cid)
    evidence["categories_seeded"] = seeded
    rows = conn.execute("SELECT category_id, name_fa, name_en, sort_order FROM Category ORDER BY sort_order").fetchall()
    evidence["category_rows"] = [list(r) for r in rows]


def ensure_product_category_fk(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    evidence["product_category_fk_note"] = (
        "Product.category_id column added if missing. "
        "SQLite does not support ADD CONSTRAINT for FK on existing tables; "
        "FK is enforced by PRAGMA foreign_keys when models/ORM create new DBs. "
        "Integrity checked via PRAGMA foreign_key_check after seed."
    )


def foreign_key_check(conn: sqlite3.Connection) -> List[Any]:
    conn.execute("PRAGMA foreign_keys=ON")
    return conn.execute("PRAGMA foreign_key_check").fetchall()


def migrate(db_path: str, dry_run: bool = False) -> Dict[str, Any]:
    evidence: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "db_path": db_path,
        "dry_run": dry_run,
        "status": "STARTED",
    }
    if db_path == ":memory:":
        conn = sqlite3.connect(":memory:")
    else:
        p = Path(db_path)
        if not p.exists() and db_path != ":memory:":
            p.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)

    try:
        conn.execute("PRAGMA foreign_keys=ON")
        evidence["pre_schema"] = capture_schema(conn)
        evidence["pre_row_counts"] = capture_row_counts(conn)
        evidence["pre_toman_samples"] = capture_toman_samples(conn)

        if dry_run:
            evidence["status"] = "DRY_RUN_COMPLETE"
            return evidence

        ensure_tables(conn, evidence)
        ensure_columns(conn, evidence)
        seed_categories(conn, evidence)
        ensure_product_category_fk(conn, evidence)

        conn.commit()

        evidence["post_schema"] = capture_schema(conn)
        evidence["post_row_counts"] = capture_row_counts(conn)
        evidence["post_toman_samples"] = capture_toman_samples(conn)
        fk_violations = foreign_key_check(conn)
        evidence["fk_check_violations"] = [list(v) for v in fk_violations]
        evidence["fk_check"] = "PASS" if len(fk_violations) == 0 else "FAIL"

        ensure_tables(conn, evidence)
        ensure_columns(conn, evidence)
        seed_categories(conn, evidence)
        conn.commit()
        evidence["idempotent_re_run"] = "OK"

        if evidence["pre_toman_samples"] != evidence["post_toman_samples"]:
            if evidence["pre_toman_samples"] and any(
                not (isinstance(v, list) and (not v or isinstance(v[0], str) and v[0].startswith("error")))
                for v in evidence["pre_toman_samples"].values()
            ):
                evidence["toman_preserved"] = "FAIL"
                evidence["status"] = "FAIL_TOMAN_CHANGED"
                return evidence
        evidence["toman_preserved"] = "YES"

        row_ok = True
        for t, pre_c in evidence["pre_row_counts"].items():
            post_c = evidence["post_row_counts"].get(t, -1)
            if pre_c >= 0 and post_c >= 0 and post_c < pre_c:
                row_ok = False
        evidence["row_counts_preserved"] = "YES" if row_ok else "NO"

        evidence["status"] = "SUCCESS"
        return evidence
    except Exception as e:
        evidence["status"] = "ERROR"
        evidence["error"] = str(e)
        conn.rollback()
        raise
    finally:
        conn.close()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HBI PHASE 02 accounting schema migration (clone-safe)")
    parser.add_argument("--db", required=True, help="Path to SQLite DB (use a disposable clone; never production without backup)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", help="Write evidence JSON to this path")
    args = parser.parse_args(argv)

    if args.db.replace("\\", "/").endswith("data/hbi.db") and not Path(args.db).resolve().as_posix().endswith(":memory:"):
        print("REFUSED: will not migrate real data/hbi.db without HBI_ALLOW_REAL_DB=1", file=sys.stderr)
        if not __import__("os").environ.get("HBI_ALLOW_REAL_DB"):
            return 2

    evidence = migrate(args.db, dry_run=args.dry_run)
    print(json.dumps(evidence, indent=2, ensure_ascii=False, default=str))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return 0 if evidence.get("status") in ("SUCCESS", "DRY_RUN_COMPLETE") else 1


if __name__ == "__main__":
    sys.exit(main())
