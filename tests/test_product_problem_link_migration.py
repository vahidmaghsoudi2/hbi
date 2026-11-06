import runpy
import sqlite3
from pathlib import Path

import pytest


def _migrate():
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "migrate_product_problem_link_assessments.py"
    )
    return runpy.run_path(str(script))["migrate"]


def _legacy_sql(*, extra: str = "") -> str:
    return f"""
        PRAGMA foreign_keys=ON;
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL,
            FOREIGN KEY(product_id) REFERENCES Product(product_id)
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL DEFAULT 'UNKNOWN',
            market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL DEFAULT 'CANDIDATE',
            semantic_basis VARCHAR NOT NULL, limitations VARCHAR NOT NULL,
            decision_basis VARCHAR NOT NULL,
            problem_map_version VARCHAR NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_id,evidence_id,problem_id,relationship_role,variant,market_region),
            FOREIGN KEY(product_id) REFERENCES Product(product_id),
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id),
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id)
        );
        {extra}
        INSERT INTO Product VALUES ('P1');
        INSERT INTO Evidence VALUES ('E1','C1','P1');
        INSERT INTO ProductProblemLink(
            link_id,product_id,variant,market_region,claim_id,evidence_id,problem_id,
            problem_type,problem_definition_ref,relationship_role,relationship_status,
            semantic_basis,limitations,decision_basis,problem_map_version
        ) VALUES (
            'L1','P1','UNKNOWN','MEXICO','C1','E1','P17','presentation','Map#P17',
            'presentation','NOT_LINKED','old basis','old limits','old decision',
            'SKIN_PROBLEM_SPACE_MAP_V0.1'
        );
    """


def test_legacy_migration_preserves_rows_custom_objects_and_wal(tmp_path):
    migrate = _migrate()
    db = tmp_path / "legacy.db"
    conn = sqlite3.connect(db)
    mode = conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
    assert mode.lower() == "wal"
    conn.execute("PRAGMA wal_autocheckpoint=0")
    conn.executescript(
        _legacy_sql(
            extra="""
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
        """
        )
    )
    conn.commit()
    conn.execute("UPDATE ProductProblemLink SET limitations = limitations WHERE link_id='L1'")
    conn.commit()
    wal_keeper = sqlite3.connect(db)
    wal_keeper.execute("BEGIN")
    assert wal_keeper.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone()[0] == 1
    conn.close()

    result = migrate(db)
    wal_keeper.close()
    assert result.startswith("MIGRATED")
    backup_path = Path(result.split("Backup: ", 1)[1])
    assert backup_path.is_file()

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT link_id, relationship_status, feature_basis, assertion_key, revision_no "
        "FROM ProductProblemLink"
    ).fetchone()
    assert row == ("L1", "NOT_LINKED", None, None, None)
    indexes = {
        r[1] for r in conn.execute('PRAGMA index_list("ProductProblemLink")')
    }
    assert "ix_custom_ppl_market" in indexes
    assert "ix_productproblemlink_product" in indexes
    assert "ix_productproblemlink_assertion" in indexes
    event_indexes = {
        r[1]
        for r in conn.execute(
            'PRAGMA index_list("ProductProblemLinkAssessmentEvent")'
        )
    }
    assert "ix_ProductProblemLinkAssessmentEvent_assertion_key" in event_indexes
    conn.execute(
        "UPDATE ProductProblemLink SET relationship_status='CANDIDATE' WHERE link_id='L1'"
    )
    assert conn.execute(
        "SELECT link_id, new_status FROM ProductProblemLinkAudit"
    ).fetchone() == ("L1", "CANDIDATE")
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()

    again = migrate(db)
    assert again.startswith("ALREADY MIGRATED")


def test_standard_hbi_indexes_accepted(tmp_path):
    migrate = _migrate()
    db = tmp_path / "standard.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        _legacy_sql(
            extra="""
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        """
        )
    )
    conn.close()
    assert migrate(db).startswith("MIGRATED")
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM ProductProblemLink").fetchone()[0] == 1
    conn.close()


def test_canonical_name_with_unique_mismatch_is_conflict(tmp_path):
    migrate = _migrate()
    db = tmp_path / "unique_mismatch.db"
    conn = sqlite3.connect(db)
    conn.executescript(_legacy_sql())
    conn.execute(
        "CREATE UNIQUE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id)"
    )
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="differ in definition"):
        migrate(db)
    conn = sqlite3.connect(db)
    cols = {r[1] for r in conn.execute('PRAGMA table_info("ProductProblemLink")')}
    assert "feature_basis" not in cols
    conn.close()


def test_canonical_name_partial_index_is_conflict(tmp_path):
    migrate = _migrate()
    db = tmp_path / "partial.db"
    conn = sqlite3.connect(db)
    conn.executescript(_legacy_sql())
    conn.execute(
        "CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id) "
        "WHERE product_id IS NOT NULL"
    )
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="differ in definition"):
        migrate(db)


def test_already_migrated_rejects_wrong_event_index_definition(tmp_path):
    migrate = _migrate()
    db = tmp_path / "wrong_event_idx.db"
    conn = sqlite3.connect(db)
    conn.executescript(_legacy_sql())
    conn.close()
    assert migrate(db).startswith("MIGRATED")
    conn = sqlite3.connect(db)
    conn.execute("DROP INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key")
    conn.execute(
        "CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key "
        "ON ProductProblemLinkAssessmentEvent(link_id)"
    )
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="canonical index mismatch"):
        migrate(db)


def test_already_migrated_repairs_missing_ppl_index(tmp_path):
    migrate = _migrate()
    db = tmp_path / "missing_ppl_idx.db"
    conn = sqlite3.connect(db)
    conn.executescript(_legacy_sql())
    conn.close()
    assert migrate(db).startswith("MIGRATED")
    conn = sqlite3.connect(db)
    conn.execute("DROP INDEX ix_productproblemlink_assertion")
    conn.commit()
    conn.close()
    result = migrate(db)
    assert result.startswith("ALREADY MIGRATED")
    conn = sqlite3.connect(db)
    indexes = {
        r[1] for r in conn.execute('PRAGMA index_list("ProductProblemLink")')
    }
    assert "ix_productproblemlink_assertion" in indexes
    conn.close()


def test_already_migrated_rejects_missing_check_constraint(tmp_path):
    migrate = _migrate()
    db = tmp_path / "missing_check.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE ProductProblemLink (
            link_id VARCHAR PRIMARY KEY,
            product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL,
            market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL,
            evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL,
            problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL,
            limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL,
            problem_map_version VARCHAR NOT NULL,
            feature_basis TEXT,
            outcome TEXT,
            assertion_key VARCHAR,
            revision_no INTEGER,
            supersedes_link_id VARCHAR,
            idempotency_key VARCHAR,
            request_fingerprint VARCHAR,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY,
            link_id VARCHAR NOT NULL,
            assertion_key VARCHAR,
            revision_no INTEGER,
            actor_id VARCHAR NOT NULL,
            actor_role VARCHAR,
            event_type VARCHAR NOT NULL,
            reason TEXT NOT NULL,
            before_state TEXT,
            after_state TEXT NOT NULL,
            correlation_id VARCHAR,
            timestamp DATETIME NOT NULL
        );
        """
    )
    conn.close()
    with pytest.raises(
        RuntimeError,
        match="CHECK pattern|CHECK fragment|missing UNIQUE|missing FK|column contract|canonical index",
    ):
        migrate(db)


def test_incomplete_event_schema_rejected(tmp_path):
    migrate = _migrate()
    db = tmp_path / "incomplete_event.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE ProductProblemLink (
            link_id VARCHAR PRIMARY KEY,
            product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL,
            market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL,
            evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL,
            problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL,
            limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL,
            problem_map_version VARCHAR NOT NULL,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR, request_fingerprint VARCHAR,
            created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL,
            CHECK (variant IN ('COLOR','NON_COLOR','UNKNOWN')),
            CHECK (relationship_role IN ('presentation','context','clinical_anchor','sequela')),
            CHECK (relationship_status IN ('CANDIDATE','NOT_LINKED','DEFERRED')),
            CHECK (revision_no IS NULL OR revision_no >= 1),
            UNIQUE(assertion_key, revision_no),
            UNIQUE(idempotency_key),
            UNIQUE(supersedes_link_id)
        );
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY,
            link_id VARCHAR NOT NULL
        );
        """
    )
    conn.close()
    with pytest.raises(RuntimeError):
        migrate(db)


def test_foreign_key_violation_restores_backup(tmp_path):
    migrate = _migrate()
    db = tmp_path / "fk.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink (
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
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL,
            limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL,
            problem_map_version VARCHAR NOT NULL,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR UNIQUE, request_fingerprint VARCHAR,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (variant IN ('COLOR','NON_COLOR','UNKNOWN')),
            CHECK (relationship_role IN ('presentation','context','clinical_anchor','sequela')),
            CHECK (relationship_status IN ('CANDIDATE','NOT_LINKED','DEFERRED')),
            CHECK (revision_no IS NULL OR revision_no >= 1),
            UNIQUE(assertion_key, revision_no),
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id),
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id),
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id)
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
        CREATE TABLE Parent(parent_id INTEGER PRIMARY KEY);
        CREATE TABLE Child(parent_id INTEGER REFERENCES Parent(parent_id));
        INSERT INTO Child(parent_id) VALUES (999);
        """
    )
    conn.close()
    with pytest.raises(RuntimeError, match="Foreign-key violations"):
        migrate(db)
    conn = sqlite3.connect(db)
    assert conn.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()


def test_required_unique_index_must_be_full_plain_and_non_partial():
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "migrate_product_problem_link_assessments.py"
    )
    module = runpy.run_path(str(script))
    check = module["_is_full_plain_unique_index"]
    base = {
        "unique": True,
        "partial": 0,
        "has_expression": False,
        "desc": [0, 0],
        "coll": ["BINARY", "BINARY"],
        "columns": ["assertion_key", "revision_no"],
    }
    assert check(base)
    assert not check({**base, "partial": 1})
    assert not check({**base, "has_expression": True})
    assert not check({**base, "desc": [0, 1]})
    assert not check({**base, "coll": ["NOCASE", "BINARY"]})


def test_migration_delete_policy_matches_orm_restrict_contract():
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "migrate_product_problem_link_assessments.py"
    )
    module = runpy.run_path(str(script))
    assert module["ALLOWED_ON_DELETE"] == frozenset({"RESTRICT"})
