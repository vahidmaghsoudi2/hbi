import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from scripts.export_seven_product_acceptance_snapshot import PRODUCT_IDS, export_snapshot


def _db(path: Path):
    c = sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE Product(product_id TEXT PRIMARY KEY,brand TEXT,product_name TEXT,product_line TEXT,identity_status TEXT,qa_verdict TEXT,status TEXT);
    CREATE TABLE Evidence(evidence_id TEXT PRIMARY KEY,product_id TEXT,claim TEXT,source_reference TEXT,qa_status TEXT,evidence_status TEXT);
    CREATE TABLE ProductKnowledge(product_knowledge_id TEXT PRIMARY KEY,product_id TEXT,known_use_cases TEXT,evidence_status TEXT);
    CREATE TABLE Inventory(inventory_id TEXT PRIMARY KEY,product_id TEXT,quantity_available INTEGER,quantity_reserved INTEGER,quantity_damaged INTEGER,stock_status TEXT);
    CREATE TABLE Recommendation(recommendation_id TEXT PRIMARY KEY,product_id TEXT,case_id TEXT,eligibility_status TEXT,evidence_refs TEXT);
    CREATE TABLE ProductProblemLink(link_id TEXT PRIMARY KEY,product_id TEXT,problem_id TEXT,relationship_status TEXT,evidence_id TEXT);
    """)
    pid = PRODUCT_IDS[0]
    c.execute("INSERT INTO Product VALUES(?,?,?,?,?,?,?)", (pid, "B", "P", "SKIN", "NEEDS_REVIEW", "PENDING", "DRAFT"))
    c.execute("INSERT INTO Product VALUES(?,?,?,?,?,?,?)", ("UNRELATED", "X", "Y", "SKIN", "VERIFIED", "VALID", "ACTIVE"))
    c.execute("INSERT INTO Evidence VALUES(?,?,?,?,?,?)", ("E1", pid, "claim", "source", "PENDING", "UNKNOWN"))
    c.execute("INSERT INTO Inventory VALUES(?,?,?,?,?,?)", ("I1", pid, 5, 1, 0, "IN_STOCK"))
    c.execute("INSERT INTO Recommendation VALUES(?,?,?,?,?)", ("R1", pid, "PRIVATE-CASE", "INELIGIBLE_PENDING_REVIEW", "E1"))
    c.commit()
    c.close()


def _sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def test_export_is_read_only_scoped_and_redacts_case_ids(tmp_path):
    db, out = tmp_path / "hbi.db", tmp_path / "snapshot.json"
    _db(db)
    before = _sha(db)
    payload = export_snapshot(db, out)
    assert _sha(db) == before
    assert payload["integrity_check"] == "ok"
    assert payload["missing_product_ids"] == list(PRODUCT_IDS[1:])
    assert payload["table_row_counts"]["Product"] == 1
    assert payload["table_row_counts"]["Evidence"] == 1
    assert payload["table_row_counts"]["Recommendation"] == 1
    assert payload["table_row_counts"]["Inventory"] == 1
    assert payload["tables"]["Inventory"][0]["inventory_id"] == "I1"
    assert payload["missing_columns"]["Product"]
    raw = out.read_text(encoding="utf-8")
    assert "UNRELATED" not in raw and "PRIVATE-CASE" not in raw
    assert json.loads(raw)["tables"]["Evidence"][0]["qa_status"] == "PENDING"
    assert payload["source_access"]["sqlite_connection_target"] == "isolated temporary copy only"
    assert payload["source_access"]["source_database_opened_by_sqlite"] is False
    assert not Path(str(db) + "-shm").exists()


def test_export_never_overwrites_existing_output(tmp_path):
    db, out = tmp_path / "hbi.db", tmp_path / "snapshot.json"
    _db(db)
    out.write_text("preserve", encoding="utf-8")
    with pytest.raises(ValueError, match="never overwrites"):
        export_snapshot(db, out)
    assert out.read_text(encoding="utf-8") == "preserve"


def test_export_rejects_missing_database(tmp_path):
    with pytest.raises(ValueError, match="existing regular file"):
        export_snapshot(tmp_path / "missing.db", tmp_path / "snapshot.json")


def test_validation_exit_code_requires_complete_tables_and_clean_foreign_keys():
    from scripts.export_seven_product_acceptance_snapshot import validation_exit_code
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": [], "missing_columns": {}, "foreign_key_violation_count": 0}) == 0
    assert validation_exit_code({"missing_product_ids": ["P1"], "missing_tables": [], "missing_columns": {}, "foreign_key_violation_count": 0}) == 2
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": ["Evidence"], "missing_columns": {}, "foreign_key_violation_count": 0}) == 3
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": [], "missing_columns": {"Product": ["status"]}, "foreign_key_violation_count": 0}) == 3
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": [], "missing_columns": {}, "foreign_key_violation_count": 1}) == 3


def test_export_reads_uncheckpointed_wal_without_touching_source_db_wal_or_shm(tmp_path):
    db, out = tmp_path / "hbi-wal.db", tmp_path / "snapshot-wal.json"
    _db(db)
    writer = sqlite3.connect(db)
    writer.execute("PRAGMA journal_mode=WAL")
    writer.execute("UPDATE Product SET product_name=? WHERE product_id=?", ("WAL-visible product", PRODUCT_IDS[0]))
    writer.commit()
    wal, shm = Path(str(db) + "-wal"), Path(str(db) + "-shm")
    assert wal.exists() and shm.exists()
    before = {"db": _sha(db), "wal": _sha(wal), "shm": _sha(shm)}
    payload = export_snapshot(db, out)
    assert {"db": _sha(db), "wal": _sha(wal), "shm": _sha(shm)} == before
    assert payload["tables"]["Product"][0]["product_name"] == "WAL-visible product"
    assert payload["source_database"]["shm_sha256"] == before["shm"]
    assert payload["source_access"]["shm_copied"] is False
    writer.close()


def test_export_fails_closed_when_rollback_journal_exists(tmp_path):
    db = tmp_path / "hbi.db"
    _db(db)
    journal = Path(str(db) + "-journal")
    journal.write_bytes(b"active-or-stale-journal")
    with pytest.raises(RuntimeError, match="rollback journal exists"):
        export_snapshot(db, tmp_path / "snapshot.json")
    assert journal.read_bytes() == b"active-or-stale-journal"


def test_export_rejects_symlink_source_and_database_sidecar_output(tmp_path):
    db, out = tmp_path / "hbi.db", tmp_path / "snapshot.json"
    _db(db)
    link = tmp_path / "hbi-link.db"
    link.symlink_to(db)
    with pytest.raises(ValueError, match="not a symlink"):
        export_snapshot(link, out)
    with pytest.raises(ValueError, match="sidecar"):
        export_snapshot(db, Path(str(db) + "-wal"))
