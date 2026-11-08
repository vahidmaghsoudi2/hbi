import hashlib, json, sqlite3
from pathlib import Path
import pytest
from scripts.export_seven_product_acceptance_snapshot import PRODUCT_IDS, export_snapshot

def _db(path: Path):
    c=sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE Product(product_id TEXT PRIMARY KEY,brand TEXT,product_name TEXT,product_line TEXT,identity_status TEXT,qa_verdict TEXT,status TEXT);
    CREATE TABLE Evidence(evidence_id TEXT PRIMARY KEY,product_id TEXT,claim TEXT,source_reference TEXT,qa_status TEXT,evidence_status TEXT);
    CREATE TABLE ProductKnowledge(product_knowledge_id TEXT PRIMARY KEY,product_id TEXT,known_use_cases TEXT,evidence_status TEXT);
    CREATE TABLE Inventory(inventory_id TEXT PRIMARY KEY,product_id TEXT,quantity_available INTEGER,quantity_reserved INTEGER,quantity_damaged INTEGER,stock_status TEXT);
    CREATE TABLE Recommendation(recommendation_id TEXT PRIMARY KEY,product_id TEXT,case_id TEXT,eligibility_status TEXT,evidence_refs TEXT);
    CREATE TABLE ProductProblemLink(link_id TEXT PRIMARY KEY,product_id TEXT,problem_id TEXT,relationship_status TEXT,evidence_id TEXT);
    """)
    pid=PRODUCT_IDS[0]
    c.execute("INSERT INTO Product VALUES(?,?,?,?,?,?,?)",(pid,"B","P","SKIN","NEEDS_REVIEW","PENDING","DRAFT"))
    c.execute("INSERT INTO Product VALUES(?,?,?,?,?,?,?)",("UNRELATED","X","Y","SKIN","VERIFIED","VALID","ACTIVE"))
    c.execute("INSERT INTO Evidence VALUES(?,?,?,?,?,?)",("E1",pid,"claim","source","PENDING","UNKNOWN"))
    c.execute("INSERT INTO Recommendation VALUES(?,?,?,?,?)",("R1",pid,"PRIVATE-CASE","INELIGIBLE_PENDING_REVIEW","E1"))
    c.commit(); c.close()

def test_export_is_read_only_scoped_and_redacts_case_ids(tmp_path):
    db=tmp_path/"hbi.db"; out=tmp_path/"snapshot.json"; _db(db)
    before=hashlib.sha256(db.read_bytes()).hexdigest()
    payload=export_snapshot(db,out)
    assert hashlib.sha256(db.read_bytes()).hexdigest()==before
    assert payload["integrity_check"]=="ok"
    assert payload["missing_product_ids"]==list(PRODUCT_IDS[1:])
    assert payload["table_row_counts"]["Product"]==1
    assert payload["table_row_counts"]["Evidence"]==1
    assert payload["table_row_counts"]["Recommendation"]==1
    raw=out.read_text(encoding="utf-8")
    assert "UNRELATED" not in raw and "PRIVATE-CASE" not in raw
    assert json.loads(raw)["tables"]["Evidence"][0]["qa_status"]=="PENDING"

def test_export_never_overwrites_existing_output(tmp_path):
    db=tmp_path/"hbi.db"; out=tmp_path/"snapshot.json"; _db(db)
    out.write_text("preserve",encoding="utf-8")
    with pytest.raises(ValueError,match="never overwrites"): export_snapshot(db,out)
    assert out.read_text(encoding="utf-8")=="preserve"

def test_export_rejects_missing_database(tmp_path):
    with pytest.raises(ValueError,match="existing regular file"):
        export_snapshot(tmp_path/"missing.db",tmp_path/"snapshot.json")


def test_validation_exit_code_requires_complete_tables_and_clean_foreign_keys():
    from scripts.export_seven_product_acceptance_snapshot import validation_exit_code
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": [], "foreign_key_violation_count": 0}) == 0
    assert validation_exit_code({"missing_product_ids": ["P1"], "missing_tables": [], "foreign_key_violation_count": 0}) == 2
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": ["Evidence"], "foreign_key_violation_count": 0}) == 3
    assert validation_exit_code({"missing_product_ids": [], "missing_tables": [], "foreign_key_violation_count": 1}) == 3


def test_export_reads_uncheckpointed_wal_without_mutating_source_or_wal(tmp_path):
    db = tmp_path / "hbi-wal.db"
    out = tmp_path / "snapshot-wal.json"
    _db(db)
    writer = sqlite3.connect(db)
    writer.execute("PRAGMA journal_mode=WAL")
    writer.execute(
        "UPDATE Product SET product_name=? WHERE product_id=?",
        ("WAL-visible product", PRODUCT_IDS[0]),
    )
    writer.commit()

    wal = Path(str(db) + "-wal")
    assert wal.exists()
    db_before = hashlib.sha256(db.read_bytes()).hexdigest()
    wal_before = hashlib.sha256(wal.read_bytes()).hexdigest()

    payload = export_snapshot(db, out)

    assert hashlib.sha256(db.read_bytes()).hexdigest() == db_before
    assert hashlib.sha256(wal.read_bytes()).hexdigest() == wal_before
    assert payload["tables"]["Product"][0]["product_name"] == "WAL-visible product"
    writer.close()


def test_export_rejects_symlink_source_and_database_sidecar_output(tmp_path):
    db = tmp_path / "hbi.db"
    out = tmp_path / "snapshot.json"
    _db(db)
    link = tmp_path / "hbi-link.db"
    link.symlink_to(db)

    with pytest.raises(ValueError, match="not a symlink"):
        export_snapshot(link, out)

    with pytest.raises(ValueError, match="sidecars"):
        export_snapshot(db, Path(str(db) + "-wal"))
