#!/usr/bin/env python3
"""HBI Accounting PHASE 02 — Schema migration (additive + SQLite table rebuild for real FKs)."""
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

REQUIRED_COLUMNS: Dict[str, List[Tuple[str, str]]] = {
    "Product": [("category_id", "VARCHAR")],
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
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def get_columns(conn: sqlite3.Connection, table: str) -> Set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info([{table}])").fetchall()}


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return table in get_tables(conn)


def foreign_key_list(conn: sqlite3.Connection, table: str) -> List[Tuple]:
    return conn.execute(f"PRAGMA foreign_key_list([{table}])").fetchall()


def has_fk_to(conn: sqlite3.Connection, table: str, parent: str, from_col: str, to_col: str) -> bool:
    return any(r[2] == parent and r[3] == from_col and r[4] == to_col for r in foreign_key_list(conn, table))


def capture_schema(conn: sqlite3.Connection) -> Dict[str, Any]:
    schema: Dict[str, Any] = {}
    for t in sorted(get_tables(conn)):
        if t.startswith("sqlite_"):
            continue
        cols = conn.execute(f"PRAGMA table_info([{t}])").fetchall()
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
    for table, cols in [
        ("Inventory", "inventory_id, purchase_price_toman, sale_price_toman"),
        ("Sale", "sale_id, total_amount_toman"),
        ("SaleItem", "sale_item_id, unit_price_toman"),
    ]:
        if not table_exists(conn, table):
            continue
        try:
            samples[table] = [list(r) for r in conn.execute(f"SELECT {cols} FROM [{table}] LIMIT {limit}").fetchall()]
        except sqlite3.Error as e:
            samples[table] = [f"error: {e}"]
    return samples


def ensure_columns(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    added = list(evidence.get("columns_added") or [])
    for table, cols in REQUIRED_COLUMNS.items():
        if not table_exists(conn, table) or table == "Product":
            continue
        existing = get_columns(conn, table)
        for col_name, col_type in cols:
            if col_name not in existing:
                conn.execute(f"ALTER TABLE [{table}] ADD COLUMN [{col_name}] {col_type}")
                added.append(f"{table}.{col_name}")
    evidence["columns_added"] = added


def ensure_tables(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    created = list(evidence.get("tables_created") or [])
    for name in ["Category", "StockMovement", "Payment", "SaleReturn", "OperationalFxRate"]:
        if name in CREATE_TABLES_SQL and not table_exists(conn, name):
            conn.execute(CREATE_TABLES_SQL[name])
            created.append(name)
    evidence["tables_created"] = created


def seed_categories(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    if not table_exists(conn, "Category"):
        evidence["categories_seeded"] = []
        return
    seeded = []
    for cid, name_fa, name_en, sort_order in OFFICIAL_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO Category (category_id, name_fa, name_en, is_active, sort_order) VALUES (?, ?, ?, 1, ?)",
            (cid, name_fa, name_en, sort_order),
        )
        seeded.append(cid)
    evidence["categories_seeded"] = seeded
    evidence["category_rows"] = [list(r) for r in conn.execute(
        "SELECT category_id, name_fa, name_en, sort_order FROM Category ORDER BY sort_order"
    ).fetchall()]


def rebuild_product_with_category_fk(conn: sqlite3.Connection, evidence: Dict[str, Any]) -> None:
    if not table_exists(conn, "Product") or not table_exists(conn, "Category"):
        evidence["product_rebuild"] = "SKIPPED"
        return
    if has_fk_to(conn, "Product", "Category", "category_id", "category_id") and "category_id" in get_columns(conn, "Product"):
        evidence["product_rebuild"] = "ALREADY_HAS_FK"
        return
    cols_info = conn.execute("PRAGMA table_info([Product])").fetchall()

    def col_def(c):
        name, ctype, notnull, dflt, pk = c[1], c[2] or "VARCHAR", c[3], c[4], c[5]
        parts = [f"[{name}]", ctype or "VARCHAR"]
        if pk or name == "product_id":
            parts.append("PRIMARY KEY")
        elif notnull:
            parts.append("NOT NULL")
        if dflt is not None:
            parts.append(f"DEFAULT {dflt}")
        return " ".join(parts)

    existing_defs = [col_def(c) for c in cols_info]
    if "category_id" not in [c[1] for c in cols_info]:
        existing_defs.append("[category_id] VARCHAR")
    create_sql = (
        "CREATE TABLE [Product__new] (\n  "
        + ",\n  ".join(existing_defs)
        + ",\n  FOREIGN KEY([category_id]) REFERENCES [Category]([category_id])\n)"
    )
    select_cols = [c[1] for c in cols_info]
    insert_cols = list(select_cols)
    if "category_id" not in select_cols:
        insert_cols.append("category_id")
        select_expr = ", ".join(f"[{c}]" for c in select_cols) + ", NULL"
    else:
        select_expr = ", ".join(f"[{c}]" for c in select_cols)

    # PRAGMA foreign_keys is a no-op inside a transaction
    conn.commit()
    conn.execute("PRAGMA foreign_keys=OFF")
    dropped_children = []
    for child in ("SaleReturn", "StockMovement", "Payment"):
        if table_exists(conn, child):
            cnt = conn.execute(f"SELECT COUNT(*) FROM [{child}]").fetchone()[0]
            if cnt == 0:
                conn.execute(f"DROP TABLE [{child}]")
                dropped_children.append(child)
    try:
        conn.execute(create_sql)
        conn.execute(
            f"INSERT INTO [Product__new] ({', '.join('['+c+']' for c in insert_cols)}) "
            f"SELECT {select_expr} FROM [Product]"
        )
        conn.execute("DROP TABLE [Product]")
        conn.execute("ALTER TABLE [Product__new] RENAME TO [Product]")
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS ix_product_category_id ON [Product]([category_id])")
        except sqlite3.Error:
            pass
        for child in dropped_children:
            if child in CREATE_TABLES_SQL:
                conn.execute(CREATE_TABLES_SQL[child])
        evidence["product_rebuild"] = "REBUILT_WITH_FK"
        evidence.setdefault("columns_added", []).append("Product.category_id")
        evidence["product_rebuild_dropped_children"] = dropped_children
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def foreign_key_check(conn: sqlite3.Connection) -> List[Any]:
    conn.execute("PRAGMA foreign_keys=ON")
    return conn.execute("PRAGMA foreign_key_check").fetchall()


def collect_fk_map(conn: sqlite3.Connection) -> Dict[str, List[Dict[str, str]]]:
    result = {}
    for t in sorted(get_tables(conn)):
        if t.startswith("sqlite_"):
            continue
        result[t] = [{"id": r[0], "seq": r[1], "table": r[2], "from": r[3], "to": r[4]} for r in foreign_key_list(conn, t)]
    return result


def migrate(db_path: str, dry_run: bool = False) -> Dict[str, Any]:
    evidence: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "db_path": db_path,
        "dry_run": dry_run,
        "status": "STARTED",
    }
    conn = sqlite3.connect(":memory:" if db_path == ":memory:" else db_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        evidence["pre_schema"] = capture_schema(conn)
        evidence["pre_row_counts"] = capture_row_counts(conn)
        evidence["pre_toman_samples"] = capture_toman_samples(conn)
        evidence["pre_fk_map"] = collect_fk_map(conn)
        if dry_run:
            evidence["status"] = "DRY_RUN_COMPLETE"
            return evidence

        ensure_tables(conn, evidence)
        seed_categories(conn, evidence)
        rebuild_product_with_category_fk(conn, evidence)
        ensure_columns(conn, evidence)

        for child, parent, fcol, tcol in [
            ("SaleReturn", "Product", "product_id", "product_id"),
            ("SaleReturn", "Sale", "sale_id", "sale_id"),
            ("Payment", "Sale", "sale_id", "sale_id"),
            ("StockMovement", "Product", "product_id", "product_id"),
        ]:
            if table_exists(conn, child) and not has_fk_to(conn, child, parent, fcol, tcol):
                cnt = conn.execute(f"SELECT COUNT(*) FROM [{child}]").fetchone()[0]
                if cnt == 0:
                    conn.execute(f"DROP TABLE [{child}]")
                    if child in CREATE_TABLES_SQL:
                        conn.execute(CREATE_TABLES_SQL[child])
                    evidence.setdefault("tables_recreated_for_fk", []).append(child)
                else:
                    evidence.setdefault("fk_rebuild_skipped_nonempty", []).append(child)

        conn.commit()
        evidence["post_schema"] = capture_schema(conn)
        evidence["post_row_counts"] = capture_row_counts(conn)
        evidence["post_toman_samples"] = capture_toman_samples(conn)
        evidence["post_fk_map"] = collect_fk_map(conn)
        fk_violations = foreign_key_check(conn)
        evidence["fk_check_violations"] = [list(v) for v in fk_violations]
        evidence["fk_check"] = "PASS" if len(fk_violations) == 0 else "FAIL"
        evidence["product_category_fk_present"] = has_fk_to(conn, "Product", "Category", "category_id", "category_id")
        evidence["salereturn_product_fk_present"] = has_fk_to(conn, "SaleReturn", "Product", "product_id", "product_id")
        evidence["salereturn_sale_fk_present"] = has_fk_to(conn, "SaleReturn", "Sale", "sale_id", "sale_id")

        ensure_tables(conn, evidence)
        seed_categories(conn, evidence)
        rebuild_product_with_category_fk(conn, evidence)
        ensure_columns(conn, evidence)
        conn.commit()
        evidence["idempotent_re_run"] = "OK"

        if evidence["pre_toman_samples"] != evidence["post_toman_samples"]:
            evidence["toman_preserved"] = "FAIL"
            evidence["status"] = "FAIL_TOMAN_CHANGED"
            return evidence
        evidence["toman_preserved"] = "YES"
        row_ok = all(
            evidence["post_row_counts"].get(t, -1) >= pre_c
            for t, pre_c in evidence["pre_row_counts"].items()
            if pre_c >= 0
        )
        evidence["row_counts_preserved"] = "YES" if row_ok else "NO"
        if not evidence.get("product_category_fk_present"):
            evidence["status"] = "FAIL_MISSING_PRODUCT_CATEGORY_FK"
            return evidence
        if evidence["fk_check"] != "PASS":
            evidence["status"] = "FAIL_FK_CHECK"
            return evidence
        evidence["status"] = "SUCCESS"
        return evidence
    except Exception as e:
        evidence["status"] = "ERROR"
        evidence["error"] = str(e)
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HBI PHASE 02 accounting schema migration (clone-safe, real SQLite FKs)")
    parser.add_argument("--db", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out")
    args = parser.parse_args(argv)
    if args.db.replace("\\", "/").endswith("data/hbi.db"):
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
