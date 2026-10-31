"""SQLite migration for append-only ProductProblemLink assessments."""
from __future__ import annotations
import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

NEW_COLUMNS = {"feature_basis", "outcome", "assertion_key", "revision_no", "supersedes_link_id", "idempotency_key", "request_fingerprint"}
LEGACY_COLUMNS = [
    "link_id", "product_id", "variant", "market_region", "claim_id", "evidence_id",
    "problem_id", "problem_type", "problem_definition_ref", "relationship_role",
    "relationship_status", "semantic_basis", "limitations", "decision_basis",
    "problem_map_version", "created_at", "updated_at",
]


def migrate(db_path: str | Path) -> str:
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(db_path)
    backup_path = db_path.with_name(
        f"{db_path.stem}.before_ppl_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    )
    shutil.copy2(db_path, backup_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 0:
            raise RuntimeError("Could not disable SQLite foreign keys before table rebuild.")
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "ProductProblemLink" not in tables:
            conn.close()
            backup_path.unlink(missing_ok=True)
            return "SKIPPED: ProductProblemLink does not exist; fresh create_all will create the new schema."
        columns = {r[1] for r in conn.execute('PRAGMA table_info("ProductProblemLink")')}
        if NEW_COLUMNS.issubset(columns):
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ProductProblemLinkAssessmentEvent (
                    event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
                    assertion_key VARCHAR NULL, revision_no INTEGER NULL,
                    actor_id VARCHAR NOT NULL, actor_role VARCHAR NULL,
                    event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
                    before_state TEXT NULL, after_state TEXT NOT NULL,
                    correlation_id VARCHAR NULL, timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp)")
            conn.commit()
            conn.execute("PRAGMA foreign_keys=ON")
            return "ALREADY MIGRATED: assessment columns and history table are present."
        if not set(LEGACY_COLUMNS).issubset(columns) or columns.intersection(NEW_COLUMNS):
            raise RuntimeError("Unexpected or partially migrated ProductProblemLink schema; manual inspection required.")

        conn.execute("BEGIN IMMEDIATE")
        conn.execute("""
            CREATE TABLE ProductProblemLink__assessment_new (
                link_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
                variant VARCHAR NOT NULL DEFAULT 'UNKNOWN', market_region VARCHAR NOT NULL,
                claim_id VARCHAR NOT NULL, evidence_id VARCHAR NOT NULL,
                problem_id VARCHAR NOT NULL, problem_type VARCHAR NOT NULL,
                problem_definition_ref VARCHAR NOT NULL, relationship_role VARCHAR NOT NULL,
                relationship_status VARCHAR NOT NULL DEFAULT 'CANDIDATE',
                feature_basis TEXT NULL, outcome TEXT NULL, semantic_basis TEXT NOT NULL,
                limitations TEXT NOT NULL, decision_basis TEXT NOT NULL,
                problem_map_version VARCHAR NOT NULL, assertion_key VARCHAR NULL,
                revision_no INTEGER NULL CHECK (revision_no IS NULL OR revision_no >= 1),
                supersedes_link_id VARCHAR NULL, idempotency_key VARCHAR NULL UNIQUE,
                request_fingerprint VARCHAR NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT ck_productproblemlink_variant CHECK (variant IN ('COLOR','NON_COLOR','UNKNOWN')),
                CONSTRAINT ck_productproblemlink_role CHECK (relationship_role IN ('presentation','context','clinical_anchor','sequela')),
                CONSTRAINT ck_productproblemlink_status CHECK (relationship_status IN ('CANDIDATE','NOT_LINKED','DEFERRED')),
                CONSTRAINT uq_productproblemlink_assertion_revision UNIQUE(assertion_key, revision_no),
                CONSTRAINT uq_productproblemlink_successor UNIQUE(supersedes_link_id),
                FOREIGN KEY(product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
                FOREIGN KEY(claim_id) REFERENCES Evidence(claim_id) ON DELETE RESTRICT,
                FOREIGN KEY(evidence_id) REFERENCES Evidence(evidence_id) ON DELETE RESTRICT
            )
        """)
        names = ", ".join(f'"{name}"' for name in LEGACY_COLUMNS)
        before_count = conn.execute('SELECT COUNT(*) FROM ProductProblemLink').fetchone()[0]
        conn.execute(
            f'INSERT INTO ProductProblemLink__assessment_new ({names}) '
            f'SELECT {names} FROM ProductProblemLink'
        )
        conn.execute('DROP TABLE ProductProblemLink')
        conn.execute('ALTER TABLE ProductProblemLink__assessment_new RENAME TO ProductProblemLink')
        conn.execute('CREATE INDEX ix_productproblemlink_product ON ProductProblemLink(product_id)')
        conn.execute('CREATE INDEX ix_productproblemlink_problem ON ProductProblemLink(problem_id)')
        conn.execute('CREATE INDEX ix_productproblemlink_status ON ProductProblemLink(relationship_status)')
        conn.execute('CREATE INDEX ix_productproblemlink_assertion ON ProductProblemLink(assertion_key)')
        conn.execute("""
            CREATE TABLE ProductProblemLinkAssessmentEvent (
                event_id VARCHAR PRIMARY KEY, link_id VARCHAR NOT NULL,
                assertion_key VARCHAR NULL, revision_no INTEGER NULL,
                actor_id VARCHAR NOT NULL, actor_role VARCHAR NULL,
                event_type VARCHAR NOT NULL, reason TEXT NOT NULL,
                before_state TEXT NULL, after_state TEXT NOT NULL,
                correlation_id VARCHAR NULL, timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute('CREATE INDEX ix_ppl_event_link_time ON ProductProblemLinkAssessmentEvent(link_id, timestamp)')
        after_count = conn.execute('SELECT COUNT(*) FROM ProductProblemLink').fetchone()[0]
        if before_count != after_count:
            raise RuntimeError(f"Legacy row count changed: {before_count} -> {after_count}")
        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON")
        if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise RuntimeError("SQLite foreign-key enforcement could not be restored.")
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(f"Foreign-key violations after migration: {violations[:10]}")
        return f"MIGRATED: preserved {after_count} legacy rows; new metadata remains NULL. Backup: {backup_path}"
    except Exception:
        try:
            conn.rollback()
        finally:
            conn.close()
        shutil.copy2(backup_path, db_path)
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
