import runpy
import sqlite3
from pathlib import Path


def test_legacy_migration_preserves_rows_and_does_not_invent_revision_metadata(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_product_problem_link_assessments.py"
    migrate = runpy.run_path(str(script))["migrate"]
    db = tmp_path / "legacy.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA wal_autocheckpoint=0")
    conn.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL, FOREIGN KEY(product_id) REFERENCES Product(product_id)
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL DEFAULT 'UNKNOWN', market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL, relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL DEFAULT 'CANDIDATE',
            semantic_basis VARCHAR NOT NULL, limitations VARCHAR NOT NULL,
            decision_basis VARCHAR NOT NULL, problem_map_version VARCHAR NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id,evidence_id,problem_id,relationship_role,variant,market_region),
            FOREIGN KEY(product_id) REFERENCES Product(product_id),
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id),
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id)
        );
        INSERT INTO Product VALUES ('P1');
        INSERT INTO Evidence VALUES ('E1','C1','P1');
        INSERT INTO ProductProblemLink(
            link_id,product_id,variant,market_region,claim_id,evidence_id,problem_id,
            problem_type,problem_definition_ref,relationship_role,relationship_status,
            semantic_basis,limitations,decision_basis,problem_map_version
        ) VALUES (
            'L1','P1','UNKNOWN','MEXICO','C1','E1','P17','presentation','Map#P17',
            'presentation','NOT_LINKED','old basis','old limits','old decision','SKIN_PROBLEM_SPACE_MAP_V0.1'
        );
    """)
    conn.commit()
    # Keep a second connection open so committed WAL pages remain outside the main DB file.
    wal_keeper = sqlite3.connect(db)
    wal_keeper.execute("BEGIN")
    assert wal_keeper.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone() == (1,)
    conn.close()
    wal_path = Path(str(db) + "-wal")
    assert wal_path.exists()

    migration_result = migrate(db)
    wal_keeper.close()
    assert migration_result.startswith("MIGRATED")
    backup_path = Path(migration_result.split("Backup: ", 1)[1])
    assert backup_path.is_file()
    backup_conn = sqlite3.connect(backup_path)
    backup_row = backup_conn.execute(
        "SELECT link_id, relationship_status FROM ProductProblemLink"
    ).fetchone()
    assert backup_row == ("L1", "NOT_LINKED")
    backup_conn.close()
    conn = sqlite3.connect(db)
    columns = {r[1] for r in conn.execute('PRAGMA table_info("ProductProblemLink")')}
    row = conn.execute(
        "SELECT link_id, relationship_status, feature_basis, outcome, assertion_key, revision_no FROM ProductProblemLink"
    ).fetchone()
    assert {"feature_basis", "outcome", "assertion_key", "revision_no"}.issubset(columns)
    assert row == ("L1", "NOT_LINKED", None, None, None, None)
    assert conn.execute("SELECT COUNT(*) FROM ProductProblemLinkAssessmentEvent").fetchone()[0] == 0
    # The old scope-only unique constraint is gone; a governed successor may reuse that scope.
    conn.execute("""
        INSERT INTO ProductProblemLink(
            link_id,product_id,variant,market_region,claim_id,evidence_id,problem_id,
            problem_type,problem_definition_ref,relationship_role,relationship_status,
            feature_basis,outcome,semantic_basis,limitations,decision_basis,
            problem_map_version,assertion_key,revision_no,supersedes_link_id,
            idempotency_key,request_fingerprint
        ) VALUES (
            'L2','P1','UNKNOWN','MEXICO','C1','E1','P17','presentation','Map#P17',
            'presentation','CANDIDATE','basis','outcome','new basis','limits','decision',
            'SKIN_PROBLEM_SPACE_MAP_V0.1','assertion-1',1,'L1','idempotency-0001','fingerprint'
        )
    """)
    assert conn.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone()[0] == 2
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()
    assert migrate(db).startswith("ALREADY MIGRATED")
