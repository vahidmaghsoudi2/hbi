import runpy
import sqlite3
from pathlib import Path

import pytest


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
        CREATE INDEX ix_custom_ppl_market ON ProductProblemLink(market_region);
        CREATE TABLE ProductProblemLinkAudit(
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id VARCHAR NOT NULL,
            new_status VARCHAR NOT NULL
        );
        CREATE TRIGGER trg_custom_ppl_status_audit
        AFTER UPDATE OF relationship_status ON ProductProblemLink
        BEGIN
            INSERT INTO ProductProblemLinkAudit(link_id, new_status)
            VALUES (NEW.link_id, NEW.relationship_status);
        END;
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
    event_indexes = {
        row[1]
        for row in conn.execute(
            'PRAGMA index_list("ProductProblemLinkAssessmentEvent")'
        )
    }
    assert "ix_ppl_event_link_time" in event_indexes
    assert "ix_ProductProblemLinkAssessmentEvent_assertion_key" in event_indexes
    ppl_indexes = {
        row[1] for row in conn.execute('PRAGMA index_list("ProductProblemLink")')
    }
    assert "ix_custom_ppl_market" in ppl_indexes
    trigger_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND name='trg_custom_ppl_status_audit'"
    ).fetchone()
    assert trigger_sql and "ProductProblemLinkAudit" in trigger_sql[0]
    conn.execute(
        "UPDATE ProductProblemLink SET relationship_status='CANDIDATE' WHERE link_id='L1'"
    )
    assert conn.execute(
        "SELECT link_id, new_status FROM ProductProblemLinkAudit"
    ).fetchone() == ("L1", "CANDIDATE")
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
    # The already-migrated path must repair a missing model-declared index too.
    conn = sqlite3.connect(db)
    conn.execute('DROP INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key')
    conn.commit()
    conn.close()
    assert migrate(db).startswith("ALREADY MIGRATED")
    conn = sqlite3.connect(db)
    repaired_event_indexes = {
        row[1]
        for row in conn.execute(
            'PRAGMA index_list("ProductProblemLinkAssessmentEvent")'
        )
    }
    assert "ix_ppl_event_link_time" in repaired_event_indexes
    assert "ix_ProductProblemLinkAssessmentEvent_assertion_key" in repaired_event_indexes
    conn.close()



def test_already_migrated_rejects_incomplete_event_table_and_restores_backup(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_product_problem_link_assessments.py"
    migrate = runpy.run_path(str(script))["migrate"]
    db = tmp_path / "malformed_already_migrated.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE ProductProblemLink (
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR, variant VARCHAR,
            market_region VARCHAR, claim_id VARCHAR, evidence_id VARCHAR,
            problem_id VARCHAR, problem_type VARCHAR, problem_definition_ref VARCHAR,
            relationship_role VARCHAR, relationship_status VARCHAR,
            semantic_basis TEXT, limitations TEXT, decision_basis TEXT,
            problem_map_version VARCHAR, created_at DATETIME, updated_at DATETIME,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR, request_fingerprint VARCHAR
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent(event_id VARCHAR PRIMARY KEY);
    """)
    conn.close()

    with pytest.raises(RuntimeError, match="schema is incomplete"):
        migrate(db)

    conn = sqlite3.connect(db)
    event_columns = {
        row[1] for row in conn.execute(
            'PRAGMA table_info("ProductProblemLinkAssessmentEvent")'
        )
    }
    assert event_columns == {"event_id"}
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' "
        "AND name='ix_ProductProblemLinkAssessmentEvent_assertion_key'"
    ).fetchone() is None
    conn.close()


def test_already_migrated_checks_foreign_key_violations_and_restores_backup(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_product_problem_link_assessments.py"
    migrate = runpy.run_path(str(script))["migrate"]
    db = tmp_path / "fk_violation_already_migrated.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        PRAGMA foreign_keys=OFF;
        CREATE TABLE ProductProblemLink (
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL DEFAULT 'UNKNOWN', market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL, relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL DEFAULT 'CANDIDATE',
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR, request_fingerprint VARCHAR
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR NULL, revision_no INTEGER NULL,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR NULL,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT NULL, after_state TEXT NOT NULL,
            correlation_id VARCHAR NULL, timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE Parent(parent_id INTEGER PRIMARY KEY);
        CREATE TABLE Child(parent_id INTEGER REFERENCES Parent(parent_id));
        INSERT INTO Child(parent_id) VALUES (999);
    """)
    conn.close()

    with pytest.raises(RuntimeError, match="Foreign-key violations"):
        migrate(db)

    conn = sqlite3.connect(db)
    assert conn.execute("PRAGMA foreign_key_check").fetchall()
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' "
        "AND name='ix_ProductProblemLinkAssessmentEvent_assertion_key'"
    ).fetchone() is None
    conn.close()



def test_already_migrated_rejects_incomplete_product_problem_link_schema(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_product_problem_link_assessments.py"
    migrate = runpy.run_path(str(script))["migrate"]
    db = tmp_path / "incomplete_ppl_schema.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE ProductProblemLink (
            link_id VARCHAR PRIMARY KEY,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR, request_fingerprint VARCHAR
        );
    """)
    conn.close()

    with pytest.raises(RuntimeError, match="ProductProblemLink schema is incomplete"):
        migrate(db)

    conn = sqlite3.connect(db)
    columns = {
        row[1] for row in conn.execute('PRAGMA table_info("ProductProblemLink")')
    }
    assert columns == {
        "link_id", "feature_basis", "outcome", "assertion_key",
        "revision_no", "supersedes_link_id", "idempotency_key",
        "request_fingerprint",
    }
    assert conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name='ProductProblemLinkAssessmentEvent'"
    ).fetchone() is None
    conn.close()
