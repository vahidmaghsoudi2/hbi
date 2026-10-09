#!/usr/bin/env python3
"""Add Customer.family_name if missing (idempotent).

Legacy behavior:
- Existing customers keep family_name = NULL.
- Identity match requires mobile + non-empty family_name on both sides.
- First/given name never participates in identity decisions.
- This script does NOT invent family_name from the display name field.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "hbi.db"


def get_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info([{table}])").fetchall()}


def migrate(db_path: Path) -> int:
    if not db_path.exists():
        print(f"DB not found: {db_path}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(db_path))
    try:
        cols = get_columns(conn, "Customer")
        if "family_name" in cols:
            print("OK: Customer.family_name already present")
            nulls = conn.execute(
                "SELECT COUNT(*) FROM Customer WHERE family_name IS NULL OR TRIM(family_name) = ''"
            ).fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM Customer").fetchone()[0]
            print(f"Legacy: {nulls}/{total} customers without family_name (match blocked until set)")
            return 0
        conn.execute("ALTER TABLE Customer ADD COLUMN family_name VARCHAR")
        conn.commit()
        print("MIGRATED: added Customer.family_name VARCHAR (nullable)")
        total = conn.execute("SELECT COUNT(*) FROM Customer").fetchone()[0]
        print(f"Legacy: {total} existing rows have family_name=NULL until staff captures it")
        return 0
    finally:
        conn.close()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = p.parse_args()
    return migrate(args.db)


if __name__ == "__main__":
    raise SystemExit(main())
