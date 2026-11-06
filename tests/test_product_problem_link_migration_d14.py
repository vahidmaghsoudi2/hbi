"""Additional D1-D4 negative coverage for ProductProblemLink migration."""
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


def _full_migrated_sql():
    return """
        PRAGMA foreign_keys=ON;
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL, market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
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
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR, timestamp DATETIME NOT NULL
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
    """


def test_canonical_name_desc_index_is_conflict(tmp_path):
    migrate = _migrate()
    db = tmp_path / "desc.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        _legacy_sql(
            extra="CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id DESC);"
        )
    )
    conn.close()
    with pytest.raises(RuntimeError, match="differ in definition"):
        migrate(db)


def test_canonical_name_collate_index_is_conflict(tmp_path):
    migrate = _migrate()
    db = tmp_path / "collate.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        _legacy_sql(
            extra="CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id COLLATE NOCASE);"
        )
    )
    conn.close()
    with pytest.raises(RuntimeError, match="differ in definition"):
        migrate(db)


def test_already_migrated_rejects_event_column_order_mismatch(tmp_path):
    migrate = _migrate()
    db = tmp_path / "event_order.db"
    conn = sqlite3.connect(db)
    conn.executescript(_full_migrated_sql())
    conn.execute("DROP INDEX ix_ppl_event_link_time")
    conn.execute(
        "CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(timestamp, link_id)"
    )
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="canonical index mismatch"):
        migrate(db)


def test_already_migrated_rejects_missing_fk(tmp_path):
    migrate = _migrate()
    db = tmp_path / "missing_fk.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL, market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
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
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR, timestamp DATETIME NOT NULL
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
        """
    )
    conn.close()
    with pytest.raises(RuntimeError, match="missing FK"):
        migrate(db)


def test_already_migrated_rejects_extra_fk(tmp_path):
    migrate = _migrate()
    db = tmp_path / "extra_fk.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL, market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
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
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT,
            FOREIGN KEY(problem_definition_ref) REFERENCES Product(product_id) ON DELETE CASCADE
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR, timestamp DATETIME NOT NULL
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
        """
    )
    conn.close()
    with pytest.raises(RuntimeError, match="unexpected extra FK"):
        migrate(db)


def test_already_migrated_rejects_cascade_on_delete(tmp_path):
    migrate = _migrate()
    db = tmp_path / "cascade.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL, market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
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
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE CASCADE,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR, timestamp DATETIME NOT NULL
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
        """
    )
    conn.close()
    with pytest.raises(RuntimeError, match="on_delete"):
        migrate(db)


def test_pre_mutation_schema_error_does_not_create_backup(tmp_path):
    migrate = _migrate()
    db = tmp_path / "pre_mut.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE Product(product_id VARCHAR PRIMARY KEY);
        CREATE TABLE Evidence(
            evidence_id VARCHAR PRIMARY KEY, claim_id VARCHAR UNIQUE,
            product_id VARCHAR NOT NULL
        );
        CREATE TABLE ProductProblemLink(
            link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
            variant VARCHAR NOT NULL, market_region VARCHAR NOT NULL,
            claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
            problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
            problem_definition_ref VARCHAR NOT NULL,
            relationship_role VARCHAR NOT NULL,
            relationship_status VARCHAR NOT NULL,
            semantic_basis TEXT NOT NULL, limitations TEXT NOT NULL,
            decision_basis TEXT NOT NULL, problem_map_version VARCHAR NOT NULL,
            feature_basis TEXT, outcome TEXT, assertion_key VARCHAR,
            revision_no INTEGER, supersedes_link_id VARCHAR,
            idempotency_key VARCHAR, request_fingerprint VARCHAR,
            created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL,
            UNIQUE(assertion_key, revision_no),
            UNIQUE(idempotency_key),
            UNIQUE(supersedes_link_id),
            FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
            FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
            FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT
        );
        CREATE TABLE ProductProblemLinkAssessmentEvent (
            event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
            assertion_key VARCHAR, revision_no INTEGER,
            actor_id VARCHAR NOT NULL, actor_role VARCHAR,
            event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
            before_state TEXT, after_state TEXT NOT NULL,
            correlation_id VARCHAR, timestamp DATETIME NOT NULL
        );
        CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
        CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
        CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
        CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key);
        CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp);
        CREATE INDEX ix_ProductProblemLinkAssessmentEvent_assertion_key
            ON ProductProblemLinkAssessmentEvent(assertion_key);
        """
    )
    conn.close()
    before = list(tmp_path.glob("*.before_ppl_assessment_*"))
    with pytest.raises(RuntimeError, match="missing expected CHECK"):
        migrate(db)
    after = list(tmp_path.glob("*.before_ppl_assessment_*"))
    assert after == before


def test_restore_preserves_custom_objects_after_fk_failure(tmp_path):
    migrate = _migrate()
    db = tmp_path / "restore_custom.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.executescript(
        _legacy_sql(
            extra="""
            CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
            CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
            CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
            CREATE INDEX custom_keep ON ProductProblemLink(market_region);
            CREATE TRIGGER trg_keep AFTER INSERT ON ProductProblemLink BEGIN SELECT 1; END;
            CREATE TABLE Parent(parent_id INTEGER PRIMARY KEY);
            CREATE TABLE Child(parent_id INTEGER REFERENCES Parent(parent_id));
            """
        )
    )
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("INSERT INTO Child(parent_id) VALUES (42)")
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError, match="Foreign-key violations"):
        migrate(db)
    conn = sqlite3.connect(db)
    idx = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='ProductProblemLink'"
        )
    }
    trg = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='ProductProblemLink'"
        )
    }
    assert "custom_keep" in idx
    assert "trg_keep" in trg
    cols = {r[1] for r in conn.execute("PRAGMA table_info('ProductProblemLink')")}
    assert "assertion_key" not in cols
    conn.close()


def test_canonical_name_expression_index_is_conflict(tmp_path):
    """Expression index (cid=-2) must not be accepted as a canonical column index."""
    migrate = _migrate()
    db = tmp_path / "expr.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        _legacy_sql(
            extra=(
                "CREATE INDEX ix_productproblemlink_product "
                "ON ProductProblemLink((lower(product_id)));"
            )
        )
    )
    conn.close()
    with pytest.raises(RuntimeError, match="differ in definition"):
        migrate(db)


def test_snapshot_restore_preserves_row_content(tmp_path):
    """Post-mutation FK failure must restore exact legacy row values, not only counts."""
    migrate = _migrate()
    db = tmp_path / "row_content.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.executescript(
        _legacy_sql(
            extra="""
            CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id);
            CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id);
            CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status);
            CREATE TABLE Parent(parent_id INTEGER PRIMARY KEY);
            CREATE TABLE Child(parent_id INTEGER REFERENCES Parent(parent_id));
            """
        )
    )
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("INSERT INTO Child(parent_id) VALUES (7)")
    conn.commit()
    before = conn.execute(
        "SELECT link_id, product_id, market_region, semantic_basis, limitations "
        "FROM ProductProblemLink WHERE link_id='L1'"
    ).fetchone()
    conn.close()
    with pytest.raises(RuntimeError, match="Foreign-key violations"):
        migrate(db)
    conn = sqlite3.connect(db)
    after = conn.execute(
        "SELECT link_id, product_id, market_region, semantic_basis, limitations "
        "FROM ProductProblemLink WHERE link_id='L1'"
    ).fetchone()
    cols = {r[1] for r in conn.execute("PRAGMA table_info('ProductProblemLink')")}
    conn.close()
    assert after == before
    assert "assertion_key" not in cols
