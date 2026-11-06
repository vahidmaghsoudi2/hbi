"""SQLite migration for append-only ProductProblemLink assessments."""
from __future__ import annotations

import argparse
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

NEW_COLUMNS = {
    "feature_basis", "outcome", "assertion_key", "revision_no",
    "supersedes_link_id", "idempotency_key", "request_fingerprint",
}
LEGACY_COLUMNS = [
    "link_id", "product_id", "variant", "market_region", "claim_id", "evidence_id",
    "problem_id", "problem_type", "problem_definition_ref", "relationship_role",
    "relationship_status", "semantic_basis", "limitations", "decision_basis",
    "problem_map_version", "created_at", "updated_at",
]
EVENT_COLUMNS = {
    "event_id", "link_id", "assertion_key", "revision_no", "actor_id",
    "actor_role", "event_type", "reason", "before_state", "after_state",
    "correlation_id", "timestamp",
}
CANONICAL_PPL_INDEXES = {
    "ix_productproblemlink_product": ("product_id",),
    "ix_productproblemlink_problem": ("problem_id",),
    "ix_productproblemlink_status": ("relationship_status",),
    "ix_productproblemlink_assertion": ("assertion_key",),
}
CANONICAL_EVENT_INDEXES = {
    "ix_ppl_event_link_time": ("link_id", "timestamp"),
    "ix_ProductProblemLinkAssessmentEvent_assertion_key": ("assertion_key",),
}
PPL_COLUMN_CONTRACT = {
    "link_id": (1, 1), "product_id": (1, 0), "variant": (1, 0), "market_region": (1, 0),
    "claim_id": (1, 0), "evidence_id": (1, 0), "problem_id": (1, 0), "problem_type": (1, 0),
    "problem_definition_ref": (1, 0), "relationship_role": (1, 0), "relationship_status": (1, 0),
    "semantic_basis": (1, 0), "limitations": (1, 0), "decision_basis": (1, 0),
    "problem_map_version": (1, 0), "feature_basis": (0, 0), "outcome": (0, 0),
    "assertion_key": (0, 0), "revision_no": (0, 0), "supersedes_link_id": (0, 0),
    "idempotency_key": (0, 0), "request_fingerprint": (0, 0), "created_at": (1, 0), "updated_at": (1, 0),
}
EVENT_COLUMN_CONTRACT = {
    "event_id": (1, 1), "link_id": (1, 0), "assertion_key": (0, 0), "revision_no": (0, 0),
    "actor_id": (1, 0), "actor_role": (0, 0), "event_type": (1, 0), "reason": (1, 0),
    "before_state": (0, 0), "after_state": (1, 0), "correlation_id": (0, 0), "timestamp": (1, 0),
}
REQUIRED_PPL_CHECK_PATTERNS = (
    r"variant\s+in\s*\(\s*'color'\s*,\s*'non_color'\s*,\s*'unknown'\s*\)",
    r"relationship_role\s+in\s*\(\s*'presentation'\s*,\s*'context'\s*,\s*'clinical_anchor'\s*,\s*'sequela'\s*\)",
    r"relationship_status\s+in\s*\(\s*'candidate'\s*,\s*'not_linked'\s*,\s*'deferred'\s*\)",
    r"revision_no\s+is\s+null\s+or\s+revision_no\s*>=\s*1",
)
REQUIRED_PPL_UNIQUE_COLUMN_SETS = (
    frozenset({"assertion_key", "revision_no"}),
    frozenset({"idempotency_key"}),
    frozenset({"supersedes_link_id"}),
)
# Match the existing ORM contract exactly. NO ACTION is not accepted as a
# substitute for RESTRICT; fail closed if the existing database differs.
REQUIRED_PPL_FK = (
    ("product_id", "Product", "product_id"),
    ("claim_id", "Evidence", "claim_id"),
    ("evidence_id", "Evidence", "evidence_id"),
)
ALLOWED_ON_DELETE = frozenset({"RESTRICT"})


def _backup_database(db_path: Path, backup_path: Path) -> None:
    source = sqlite3.connect(str(db_path), timeout=30)
    destination = sqlite3.connect(str(backup_path), timeout=30)
    try:
        source.backup(destination)
        integrity = destination.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise RuntimeError(f"SQLite backup integrity check failed: {integrity}")
        destination.commit()
    finally:
        destination.close()
        source.close()


def _norm_sql(sql: Optional[str]) -> str:
    if not sql:
        return ""
    text = sql.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.replace('"', "").replace("`", "")
    text = re.sub(r"\s*,\s*", ",", text)
    text = re.sub(r"\s*\(\s*", "(", text)
    text = re.sub(r"\s*\)\s*", ")", text)
    return text


def _index_meta(conn: sqlite3.Connection, table: str) -> Dict[str, dict]:
    """Collect full index metadata using index_list + index_xinfo + sqlite_master.sql."""
    result: Dict[str, dict] = {}
    for row in conn.execute(f'PRAGMA index_list("{table}")').fetchall():
        name = row[1]
        unique = int(row[2])
        origin = row[3]
        partial = int(row[4]) if len(row) > 4 else 0
        if origin == "pk":
            continue
        xinfo_rows = sorted(
            conn.execute(f'PRAGMA index_xinfo("{name}")').fetchall(),
            key=lambda i: int(i[0]),
        )
        key_cols: List[str] = []
        key_desc: List[int] = []
        key_coll: List[str] = []
        has_expression = False
        for xrow in xinfo_rows:
            cid = int(xrow[1]) if xrow[1] is not None else -1
            col_name = xrow[2]
            desc = int(xrow[3]) if xrow[3] is not None else 0
            coll = (xrow[4] or "").strip()
            is_key = int(xrow[5]) if len(xrow) > 5 and xrow[5] is not None else 1
            if is_key != 1:
                continue
            if cid == -2 or col_name is None:
                has_expression = True
                key_cols.append(f"expr:{cid}")
            else:
                key_cols.append(str(col_name))
            key_desc.append(desc)
            key_coll.append(coll)
        sql_row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name=?", (name,)
        ).fetchone()
        result[name] = {
            "unique": unique,
            "partial": partial,
            "columns": tuple(key_cols),
            "desc": tuple(key_desc),
            "coll": tuple(key_coll),
            "has_expression": has_expression,
            "sql": sql_row[0] if sql_row else None,
            "origin": origin,
        }
    return result


def _index_definition_matches(
    meta: dict, expected_columns: Sequence[str], *, expect_unique: bool = False
) -> bool:
    if meta.get("has_expression"):
        return False
    if tuple(meta.get("columns") or ()) != tuple(expected_columns):
        return False
    if bool(meta.get("unique")) != bool(expect_unique):
        return False
    if int(meta.get("partial") or 0) != 0:
        return False
    descs = meta.get("desc") or ()
    if any(int(d) != 0 for d in descs):
        return False
    colls = meta.get("coll") or ()
    for coll in colls:
        c = (coll or "").strip().upper()
        # Canonical indexes accept only default BINARY collation (empty or BINARY).
        if c not in {"", "BINARY"}:
            return False
    sql = _norm_sql(meta.get("sql"))
    if not sql:
        return False
    if " where " in sql or " collate " in sql:
        return False
    for col in expected_columns:
        if re.search(rf"\b{re.escape(col.lower())}\s+desc\b", sql):
            return False
    if not expect_unique and sql.startswith("create unique index"):
        return False
    return True


def _describe_index_mismatch(name: str, meta: dict, expected_columns: Sequence[str]) -> str:
    return (
        f"{name} (columns={meta.get('columns')}, expected={tuple(expected_columns)}, "
        f"unique={meta.get('unique')}, partial={meta.get('partial')}, "
        f"desc={meta.get('desc')}, coll={meta.get('coll')}, "
        f"expr={meta.get('has_expression')}, sql={meta.get('sql')!r})"
    )


def _collect_preservable_objects(conn: sqlite3.Connection) -> List[Tuple[str, str, str]]:
    rows = conn.execute(
        """SELECT type, name, sql FROM sqlite_master
           WHERE tbl_name='ProductProblemLink' AND type IN ('index','trigger') AND sql IS NOT NULL
           ORDER BY type, name"""
    ).fetchall()
    index_meta = _index_meta(conn, "ProductProblemLink")
    preserve: List[Tuple[str, str, str]] = []
    conflicts: List[str] = []
    for object_type, name, sql in rows:
        if object_type == "index" and name in CANONICAL_PPL_INDEXES:
            meta = index_meta.get(name)
            expected = CANONICAL_PPL_INDEXES[name]
            if meta and _index_definition_matches(meta, expected, expect_unique=False):
                continue
            conflicts.append(
                _describe_index_mismatch(name, meta or {}, expected)
                if meta else f"{name} (missing pragma metadata)"
            )
            continue
        preserve.append((object_type, name, sql))
    if conflicts:
        raise RuntimeError(
            "Legacy ProductProblemLink has index names that collide with migration-managed indexes but differ in definition: "
            f"{conflicts}; manual inspection required."
        )
    return preserve


def _column_map(conn: sqlite3.Connection, table: str) -> Dict[str, Tuple[Any, ...]]:
    return {
        row[1]: (row[2], int(row[3]), row[4], int(row[5]))
        for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    }


def _validate_columns(conn: sqlite3.Connection, table: str, contract: Dict[str, Tuple[int, int]]) -> None:
    cols = _column_map(conn, table)
    missing = [name for name in contract if name not in cols]
    if missing:
        raise RuntimeError(f"{table} missing columns {missing}; manual inspection required.")
    for name, (notnull, pk) in contract.items():
        _ctype, actual_notnull, _dflt, actual_pk = cols[name]
        if int(actual_pk) != int(pk):
            raise RuntimeError(f"{table}.{name} contract mismatch pk expected={pk} actual={actual_pk}")
        if int(pk) == 1:
            continue
        if int(actual_notnull) != int(notnull):
            raise RuntimeError(
                f"{table}.{name} contract mismatch notnull expected={notnull} actual={actual_notnull}"
            )


def _table_sql(conn: sqlite3.Connection, table: str) -> str:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row[0] or "" if row else ""


def _validate_ppl_fk(conn: sqlite3.Connection) -> None:
    rows = conn.execute('PRAGMA foreign_key_list("ProductProblemLink")').fetchall()
    observed: Dict[Tuple[str, str, str], str] = {}
    for row in rows:
        ref_table = row[2]
        from_col = row[3]
        to_col = row[4]
        on_delete = (row[6] or "NO ACTION").upper().replace("_", " ")
        key = (from_col, ref_table, to_col)
        if key in observed:
            raise RuntimeError(
                f"ProductProblemLink has duplicate FK for {from_col}->{ref_table}.{to_col}; manual inspection required."
            )
        observed[key] = on_delete
    required_keys = {(f, t, c) for f, t, c in REQUIRED_PPL_FK}
    for from_col, ref_table, to_col in REQUIRED_PPL_FK:
        key = (from_col, ref_table, to_col)
        if key not in observed:
            raise RuntimeError(
                f"ProductProblemLink missing FK {from_col}->{ref_table}.{to_col}; manual inspection required."
            )
        on_delete = observed[key]
        if on_delete not in ALLOWED_ON_DELETE:
            raise RuntimeError(
                f"ProductProblemLink FK {from_col}->{ref_table}.{to_col} has on_delete={on_delete!r}; "
                f"expected one of {sorted(ALLOWED_ON_DELETE)} (ORM ondelete=RESTRICT)."
            )
    extras = [k for k in observed if k not in required_keys]
    if extras:
        raise RuntimeError(
            f"ProductProblemLink has unexpected extra FK(s) {extras}; manual inspection required."
        )
    if len(observed) != len(REQUIRED_PPL_FK):
        raise RuntimeError(
            f"ProductProblemLink FK count {len(observed)} != {len(REQUIRED_PPL_FK)}; manual inspection required."
        )


def _is_full_plain_unique_index(meta: Dict[str, Any]) -> bool:
    return bool(
        meta.get("unique")
        and int(meta.get("partial") or 0) == 0
        and not meta.get("has_expression")
        and not any(meta.get("desc") or [])
        and all((coll or "BINARY").upper() == "BINARY" for coll in meta.get("coll") or [])
    )


def _validate_ppl_constraints(conn: sqlite3.Connection) -> None:
    sql = _norm_sql(_table_sql(conn, "ProductProblemLink"))
    if not sql:
        raise RuntimeError("ProductProblemLink table SQL missing from sqlite_master.")
    for pattern in REQUIRED_PPL_CHECK_PATTERNS:
        if re.search(pattern, sql, flags=re.IGNORECASE) is None:
            raise RuntimeError(
                f"ProductProblemLink missing expected CHECK pattern {pattern!r}; manual inspection required."
            )
    index_meta = _index_meta(conn, "ProductProblemLink")
    unique_col_sets = set()
    for meta in index_meta.values():
        if _is_full_plain_unique_index(meta):
            unique_col_sets.add(frozenset(meta["columns"]))
    for match in re.finditer(r"unique\s*\(([^)]+)\)", sql):
        parts = tuple(p.strip().split()[0] for p in match.group(1).split(",") if p.strip())
        unique_col_sets.add(frozenset(parts))
    for required in REQUIRED_PPL_UNIQUE_COLUMN_SETS:
        if required not in unique_col_sets:
            raise RuntimeError(
                f"ProductProblemLink missing UNIQUE on {sorted(required)}; manual inspection required."
            )
    _validate_ppl_fk(conn)


def _validate_canonical_indexes(
    conn: sqlite3.Connection, table: str, expected: Dict[str, Tuple[str, ...]], *, allow_missing: bool = False
) -> List[str]:
    meta_map = _index_meta(conn, table)
    missing: List[str] = []
    conflicts: List[str] = []
    for name, columns in expected.items():
        meta = meta_map.get(name)
        if meta is None:
            (missing if allow_missing else conflicts).append(
                name if allow_missing else f"{name} missing"
            )
            continue
        if not _index_definition_matches(meta, columns, expect_unique=False):
            conflicts.append(_describe_index_mismatch(name, meta, columns))
    if conflicts:
        raise RuntimeError(
            f"{table} canonical index mismatch: {conflicts}; manual inspection required."
        )
    return missing


def _verify_foreign_keys(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys=ON")
    if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise RuntimeError("SQLite foreign-key enforcement could not be restored.")
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise RuntimeError(f"Foreign-key violations after migration: {violations[:10]}")


def _list_user_tables(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def _table_row_fingerprint_columns(
    conn: sqlite3.Connection, table: str, columns: List[str]
) -> List[Tuple[Any, ...]]:
    if not columns:
        return []
    col_list = ", ".join(f'"{column}"' for column in columns)
    order = ", ".join(f'"{column}"' for column in columns)
    rows = conn.execute(f'SELECT {col_list} FROM "{table}" ORDER BY {order}').fetchall()
    return [tuple(row) for row in rows]


def _table_row_fingerprint(conn: sqlite3.Connection, table: str) -> List[Tuple[Any, ...]]:
    """Ordered full-row fingerprint so restore proves data content, not only counts."""
    cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")').fetchall()]
    return _table_row_fingerprint_columns(conn, table, cols)


def _capture_snapshot(conn: sqlite3.Connection) -> Dict[str, Any]:
    integrity = conn.execute("PRAGMA integrity_check").fetchone()
    fk_check = [tuple(r) for r in conn.execute("PRAGMA foreign_key_check").fetchall()]
    tables = _list_user_tables(conn)
    table_sql: Dict[str, str] = {}
    columns: Dict[str, List[str]] = {}
    counts: Dict[str, int] = {}
    rows: Dict[str, List[Tuple[Any, ...]]] = {}
    indexes: Dict[str, Dict[str, dict]] = {}
    triggers: List[Tuple[str, str, str]] = []
    for table in tables:
        table_sql[table] = _table_sql(conn, table) or ""
        columns[table] = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()]
        counts[table] = int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
        rows[table] = _table_row_fingerprint(conn, table)
        indexes[table] = {
            name: {
                "unique": meta["unique"],
                "partial": meta["partial"],
                "columns": list(meta["columns"]),
                "desc": list(meta["desc"]),
                "coll": list(meta["coll"]),
                "has_expression": meta["has_expression"],
                "sql": meta["sql"],
            }
            for name, meta in _index_meta(conn, table).items()
        }
    for row in conn.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name"
    ).fetchall():
        triggers.append((row[1], row[2], row[3] or ""))
    return {
        "integrity": integrity[0] if integrity else None,
        "fk_check": fk_check,
        "tables": tables,
        "table_sql": table_sql,
        "columns": columns,
        "counts": counts,
        "rows": rows,
        "indexes": indexes,
        "triggers": triggers,
    }


def _snapshots_equal(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    diffs: List[str] = []
    for key in (
        "integrity", "fk_check", "tables", "table_sql", "columns", "counts", "rows", "indexes", "triggers",
    ):
        if before.get(key) != after.get(key):
            diffs.append(key)
    return diffs

def _verify_successful_migration(before: Dict[str, Any], conn: sqlite3.Connection) -> None:
    """Verify successful migration preserves every legacy row and unrelated table."""
    after = _capture_snapshot(conn)
    before_tables = set(before["tables"])
    after_tables = set(after["tables"])
    expected_tables = before_tables | {"ProductProblemLinkAssessmentEvent"}
    if after_tables != expected_tables:
        raise RuntimeError(
            f"Unexpected table changes during migration: before={sorted(before_tables)}, after={sorted(after_tables)}"
        )
    if before.get("integrity") != "ok" or after.get("integrity") != "ok":
        raise RuntimeError("SQLite integrity_check must be ok before and after migration.")
    if before.get("fk_check") or after.get("fk_check"):
        raise RuntimeError("Foreign-key violations must be absent before and after migration.")
    if before.get("triggers") != after.get("triggers"):
        raise RuntimeError("Trigger definitions changed during ProductProblemLink migration.")

    for table in before_tables - {"ProductProblemLink", "ProductProblemLinkAssessmentEvent"}:
        for key in ("table_sql", "columns", "counts", "rows", "indexes"):
            if before[key][table] != after[key][table]:
                raise RuntimeError(f"Unrelated table {table} changed in {key} during migration.")

    event_table = "ProductProblemLinkAssessmentEvent"
    if event_table in before_tables:
        for key in ("table_sql", "columns", "counts", "rows"):
            if before[key][event_table] != after[key][event_table]:
                raise RuntimeError(f"Existing event history changed in {key} during migration.")
        canonical_event_names = set(CANONICAL_EVENT_INDEXES)
        before_event_custom = {
            name: meta for name, meta in before["indexes"][event_table].items()
            if name not in canonical_event_names and not name.startswith("sqlite_autoindex")
        }
        after_event_custom = {
            name: meta for name, meta in after["indexes"][event_table].items()
            if name not in canonical_event_names and not name.startswith("sqlite_autoindex")
        }
        if before_event_custom != after_event_custom:
            raise RuntimeError("Custom event-history index definitions changed during migration.")
    elif after["counts"].get(event_table) != 0:
        raise RuntimeError("New assessment event history must be empty after schema-only migration.")

    legacy_columns = before["columns"].get("ProductProblemLink", [])
    before_legacy_rows = before["rows"].get("ProductProblemLink", [])
    after_legacy_rows = _table_row_fingerprint_columns(conn, "ProductProblemLink", legacy_columns)
    if before_legacy_rows != after_legacy_rows:
        raise RuntimeError("Legacy ProductProblemLink row values changed during migration.")

    canonical_names = set(CANONICAL_PPL_INDEXES)
    before_custom = {
        name: meta
        for name, meta in before["indexes"]["ProductProblemLink"].items()
        if name not in canonical_names and not name.startswith("sqlite_autoindex")
    }
    after_custom = {
        name: meta
        for name, meta in after["indexes"]["ProductProblemLink"].items()
        if name not in canonical_names and not name.startswith("sqlite_autoindex")
    }
    if before_custom != after_custom:
        raise RuntimeError("Custom ProductProblemLink index definitions changed during migration.")

    if after["counts"].get("ProductProblemLinkAssessmentEvent") != 0:
        raise RuntimeError("New assessment event history must be empty after schema-only migration.")
    metadata_columns = (
        "feature_basis", "outcome", "assertion_key", "revision_no",
        "supersedes_link_id", "idempotency_key", "request_fingerprint",
    )
    for column in metadata_columns:
        count = conn.execute(
            f'SELECT COUNT(*) FROM "ProductProblemLink" WHERE "{column}" IS NOT NULL'
        ).fetchone()[0]
        if count:
            raise RuntimeError(
                f"Legacy migration unexpectedly populated {column} for {count} rows."
            )


def _restore_database(
    backup_path: Path,
    db_path: Path,
    expected_snapshot: Optional[Dict[str, Any]] = None,
) -> None:
    source = sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True, timeout=30)
    destination = sqlite3.connect(str(db_path), timeout=30)
    try:
        source.backup(destination)
        destination.commit()
        integrity = destination.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise RuntimeError(f"SQLite restore integrity check failed: {integrity}")
        if expected_snapshot is not None:
            after = _capture_snapshot(destination)
            diffs = _snapshots_equal(expected_snapshot, after)
            if diffs:
                raise RuntimeError(
                    f"Restore snapshot mismatch on fields {diffs}; backup may be incomplete."
                )
    finally:
        destination.close()
        source.close()


def _create_event_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE ProductProblemLinkAssessmentEvent (
        event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL, assertion_key VARCHAR NULL,
        revision_no INTEGER NULL, actor_id VARCHAR NOT NULL, actor_role VARCHAR NULL,
        event_type VARCHAR NOT NULL, reason TEXT NOT NULL, before_state TEXT NULL,
        after_state TEXT NOT NULL, correlation_id VARCHAR NULL,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
    )


def _create_event_indexes(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp)"
    )
    conn.execute(
        "CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key ON ProductProblemLinkAssessmentEvent(assertion_key)"
    )


def _create_ppl_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id)")
    conn.execute("CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id)")
    conn.execute("CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status)")
    conn.execute("CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key)")


def _handle_already_migrated(conn: sqlite3.Connection, tables: set) -> str:
    _validate_columns(conn, "ProductProblemLink", PPL_COLUMN_CONTRACT)
    _validate_ppl_constraints(conn)
    missing_ppl = _validate_canonical_indexes(
        conn, "ProductProblemLink", CANONICAL_PPL_INDEXES, allow_missing=True
    )
    if "ProductProblemLinkAssessmentEvent" not in tables:
        needs_event_table, missing_event = True, list(CANONICAL_EVENT_INDEXES)
    else:
        needs_event_table = False
        _validate_columns(conn, "ProductProblemLinkAssessmentEvent", EVENT_COLUMN_CONTRACT)
        missing_event = _validate_canonical_indexes(
            conn, "ProductProblemLinkAssessmentEvent", CANONICAL_EVENT_INDEXES, allow_missing=True
        )
    if not (missing_ppl or missing_event or needs_event_table):
        _verify_foreign_keys(conn)
        return (
            "ALREADY MIGRATED: assessment columns, history table, indexes, constraints, "
            "and foreign keys verified."
        )
    if needs_event_table:
        _create_event_table(conn)
        _create_event_indexes(conn)
        missing_event = []
    for name in missing_event:
        cols = ", ".join(CANONICAL_EVENT_INDEXES[name])
        conn.execute(f'CREATE INDEX "{name}" ON ProductProblemLinkAssessmentEvent({cols})')
    for name in missing_ppl:
        cols = ", ".join(CANONICAL_PPL_INDEXES[name])
        conn.execute(f'CREATE INDEX "{name}" ON ProductProblemLink({cols})')
    _validate_columns(conn, "ProductProblemLink", PPL_COLUMN_CONTRACT)
    _validate_ppl_constraints(conn)
    _validate_canonical_indexes(conn, "ProductProblemLink", CANONICAL_PPL_INDEXES, allow_missing=False)
    _validate_columns(conn, "ProductProblemLinkAssessmentEvent", EVENT_COLUMN_CONTRACT)
    _validate_canonical_indexes(
        conn, "ProductProblemLinkAssessmentEvent", CANONICAL_EVENT_INDEXES, allow_missing=False
    )
    conn.commit()
    _verify_foreign_keys(conn)
    return "ALREADY MIGRATED: assessment schema verified; safe missing indexes/tables repaired."


def _probe_already_state(
    conn: sqlite3.Connection, tables: set
) -> Tuple[bool, List[str], List[str], bool]:
    _validate_columns(conn, "ProductProblemLink", PPL_COLUMN_CONTRACT)
    _validate_ppl_constraints(conn)
    missing_ppl = _validate_canonical_indexes(
        conn, "ProductProblemLink", CANONICAL_PPL_INDEXES, allow_missing=True
    )
    if "ProductProblemLinkAssessmentEvent" not in tables:
        return False, missing_ppl, list(CANONICAL_EVENT_INDEXES), True
    _validate_columns(conn, "ProductProblemLinkAssessmentEvent", EVENT_COLUMN_CONTRACT)
    missing_event = _validate_canonical_indexes(
        conn, "ProductProblemLinkAssessmentEvent", CANONICAL_EVENT_INDEXES, allow_missing=True
    )
    if not missing_ppl and not missing_event:
        _verify_foreign_keys(conn)
        return True, [], [], False
    return False, missing_ppl, missing_event, False


def migrate(db_path: str | Path) -> str:
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(db_path)

    probe = sqlite3.connect(str(db_path))
    snapshot: Optional[Dict[str, Any]] = None
    custom_objects: List[Tuple[str, str, str]] = []
    try:
        probe.execute("PRAGMA foreign_keys=OFF")
        tables = {r[0] for r in probe.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "ProductProblemLink" not in tables:
            return (
                "SKIPPED: ProductProblemLink does not exist; "
                "fresh create_all will create the new schema."
            )
        columns = {r[1] for r in probe.execute('PRAGMA table_info("ProductProblemLink")')}

        if NEW_COLUMNS.issubset(columns):
            fully_ok, missing_ppl, missing_event, needs_event = _probe_already_state(probe, tables)
            if fully_ok:
                return (
                    "ALREADY MIGRATED: assessment columns, history table, indexes, constraints, "
                    "and foreign keys verified."
                )
            snapshot = _capture_snapshot(probe)
            probe.close()
            probe = None
            backup_path = db_path.with_name(
                f"{db_path.stem}.before_ppl_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{db_path.suffix}"
            )
            _backup_database(db_path, backup_path)
            mutation_started = False
            conn = sqlite3.connect(str(db_path))
            try:
                conn.execute("PRAGMA foreign_keys=OFF")
                tables = {
                    r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                }
                mutation_started = True
                return _handle_already_migrated(conn, tables)
            except Exception:
                try:
                    conn.rollback()
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if mutation_started:
                    _restore_database(backup_path, db_path, expected_snapshot=snapshot)
                raise
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        if not set(LEGACY_COLUMNS).issubset(columns) or columns.intersection(NEW_COLUMNS):
            raise RuntimeError(
                "Unexpected or partially migrated ProductProblemLink schema; manual inspection required."
            )

        custom_objects = _collect_preservable_objects(probe)
        snapshot = _capture_snapshot(probe)
    finally:
        if probe is not None:
            try:
                probe.close()
            except Exception:
                pass

    backup_path = db_path.with_name(
        f"{db_path.stem}.before_ppl_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{db_path.suffix}"
    )
    _backup_database(db_path, backup_path)
    mutation_started = False
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 0:
            raise RuntimeError("Could not disable SQLite foreign keys before table rebuild.")
        conn.execute("BEGIN IMMEDIATE")
        mutation_started = True
        conn.execute(
            """CREATE TABLE ProductProblemLink__assessment_new (
            link_id VARCHAR PRIMARY KEY,
            product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL DEFAULT 'UNKNOWN',
            market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL,
            evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL,
            problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL DEFAULT 'CANDIDATE',
            semantic_basis TEXT NOT NULL,
            limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL,
            problem_map_version VARCHAR NOT NULL,
            feature_basis TEXT NULL,
            outcome TEXT NULL,
            assertion_key VARCHAR NULL,
            revision_no INTEGER NULL,
            supersedes_link_id VARCHAR NULL,
            idempotency_key VARCHAR NULL,
            request_fingerprint VARCHAR NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT ck_productproblemlink_variant CHECK (variant IN ('COLOR','NON_COLOR','UNKNOWN')),
            CONSTRAINT ck_productproblemlink_role CHECK (relationship_role IN ('presentation','context','clinical_anchor','sequela')),
            CONSTRAINT ck_productproblemlink_status CHECK (relationship_status IN ('CANDIDATE','NOT_LINKED','DEFERRED')),
            CONSTRAINT ck_productproblemlink_revision CHECK (revision_no IS NULL OR revision_no >= 1),
            CONSTRAINT uq_productproblemlink_assertion_revision UNIQUE(assertion_key, revision_no),
            CONSTRAINT uq_productproblemlink_idempotency UNIQUE(idempotency_key),
            CONSTRAINT uq_productproblemlink_successor UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT)"""
        )
        names = ", ".join(f'"{n}"' for n in LEGACY_COLUMNS)
        before_count = conn.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone()[0]
        conn.execute(
            f"INSERT INTO ProductProblemLink__assessment_new ({names}) SELECT {names} FROM ProductProblemLink"
        )
        conn.execute("DROP TABLE ProductProblemLink")
        conn.execute("ALTER TABLE ProductProblemLink__assessment_new RENAME TO ProductProblemLink")
        _create_ppl_indexes(conn)
        for _t, _n, object_sql in custom_objects:
            conn.execute(object_sql)
        _create_event_table(conn)
        _create_event_indexes(conn)
        after_count = conn.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone()[0]
        if before_count != after_count:
            raise RuntimeError(f"Legacy row count changed: {before_count} -> {after_count}")
        _validate_columns(conn, "ProductProblemLink", PPL_COLUMN_CONTRACT)
        _validate_ppl_constraints(conn)
        _validate_canonical_indexes(
            conn, "ProductProblemLink", CANONICAL_PPL_INDEXES, allow_missing=False
        )
        _validate_columns(conn, "ProductProblemLinkAssessmentEvent", EVENT_COLUMN_CONTRACT)
        _validate_canonical_indexes(
            conn, "ProductProblemLinkAssessmentEvent", CANONICAL_EVENT_INDEXES, allow_missing=False
        )
        _verify_successful_migration(snapshot, conn)
        conn.commit()
        _verify_foreign_keys(conn)
        return (
            f"MIGRATED: preserved {after_count} legacy rows; new metadata remains NULL. "
            f"Backup: {backup_path}"
        )
    except Exception:
        try:
            conn.rollback()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        if mutation_started:
            _restore_database(backup_path, db_path, expected_snapshot=snapshot)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/hbi.db")
    print(migrate(parser.parse_args().db))
