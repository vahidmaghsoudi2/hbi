"""Export product-scoped acceptance evidence without modifying the local HBI SQLite database."""
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, tempfile
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_IDS = (
    "HBI-PROD-FE320FA135B843B6", "HBI-PROD-2CC249240D504453",
    "HBI-PROD-C29AA2F410A84CCA", "HBI-PROD-7F55ED88F41144F1",
    "HBI-PROD-96788ADC488942E3", "HBI-PROD-70EEE418BE0F4DAB",
    "HBI-PROD-22C55A8223A945A6",
)
COLUMNS = {
 "Product": "product_id brand product_name product_line variant size_value size_unit barcode_gtin market_region country_of_origin packaging_version identity_status identity_confidence identity_source_refs qa_verdict qa_reviewed_at qa_notes status created_at updated_at",
 "Evidence": "evidence_id product_id claim_id source_type source_reference claim field market_region notes claim_type evidence_strength evidence_status conflict_status source_date evidence_date qa_status created_at",
 "ProductKnowledge": "product_knowledge_id product_id ingredients ingredient_roles claimed_benefits known_use_cases contraindications usage_instructions manufacturer_claims other_attributes evidence_refs evidence_status domain_evidence_status knowledge_confidence created_at updated_at",
 "Inventory": "product_id quantity_available quantity_reserved quantity_damaged stock_status updated_at",
 "Recommendation": "recommendation_id product_id need_match_score evidence_score eligibility_status ranking_score ranking_reasons exclusion_reasons evidence_refs warnings created_at",
 "ProductProblemLink": "link_id product_id variant market_region claim_id evidence_id problem_id problem_type problem_definition_ref relationship_role relationship_status feature_basis outcome semantic_basis limitations decision_basis problem_map_version assertion_key revision_no supersedes_link_id created_at updated_at",
}

def _hash(path: Path):
    if not path.exists(): return None
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def _state(db: Path):
    wal=Path(str(db)+"-wal")
    return {"database_sha256":_hash(db),"database_bytes":db.stat().st_size,
            "wal_sha256":_hash(wal),"wal_bytes":wal.stat().st_size if wal.exists() else 0}

def export_snapshot(database_path, output_path):
    db=Path(database_path).expanduser()
    out=Path(output_path).expanduser()
    if not db.is_file() or db.is_symlink():
        raise ValueError("Source database must be an existing regular file, not a symlink.")
    if out.exists() or out.is_symlink():
        raise ValueError("Output already exists; choose a new path. The exporter never overwrites.")
    if db.resolve()==out.resolve() or out.resolve() in {
        Path(str(db)+"-wal").resolve(), Path(str(db)+"-shm").resolve()
    }:
        raise ValueError("Output must not target the source database or its SQLite sidecars.")
    before=_state(db)
    conn=sqlite3.connect(db.resolve().as_uri()+"?mode=ro", uri=True)
    conn.row_factory=sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        conn.execute("BEGIN")
        integrity=conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity!="ok": raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
        existing={r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        tables={}
        missing_tables=[]
        for table, allowed in COLUMNS.items():
            if table not in existing:
                missing_tables.append(table); tables[table]=[]; continue
            present={r["name"] for r in conn.execute(f'PRAGMA table_info("{table}")')}
            cols=[c for c in allowed.split() if c in present]
            if "product_id" not in cols:
                tables[table]=[]; continue
            select=", ".join(f'"{c}"' for c in cols)
            marks=", ".join("?" for _ in PRODUCT_IDS)
            rows=conn.execute(f'SELECT {select} FROM "{table}" WHERE product_id IN ({marks})', PRODUCT_IDS)
            tables[table]=[dict(row) for row in rows]
        found={r.get("product_id") for r in tables["Product"]}
        missing=[pid for pid in PRODUCT_IDS if pid not in found]
        fk_issues=conn.execute("PRAGMA foreign_key_check").fetchall()
        conn.commit()
    finally:
        conn.close()
    after=_state(db)
    if before!=after: raise RuntimeError("Source DB/WAL changed during export; snapshot refused.")
    payload={
      "snapshot_kind":"HBI_SEVEN_PRODUCT_READ_ONLY_ACCEPTANCE_BASELINE",
      "exported_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "source_database_name":db.name,"source_database":before,
      "integrity_check":integrity,"foreign_key_violation_count":len(fk_issues),
      "canonical_product_ids":list(PRODUCT_IDS),"missing_product_ids":missing,
      "missing_tables":missing_tables,
      "table_row_counts":{k:len(v) for k,v in tables.items()},
      "tables":tables,
      "privacy":{"scope":"canonical seven product IDs only",
                 "excluded":["Case","Customer","case_id","customer_id","customer identifiers"]},
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:
            json.dump(payload,f,ensure_ascii=False,indent=2,default=str); f.write("\n")
            f.flush(); os.fsync(f.fileno())
    except Exception:
        try: out.unlink()
        except OSError: pass
        raise
    return payload

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database",required=True,help="Local SQLite database path")
    parser.add_argument("--output",default="hbi-seven-product-acceptance-snapshot.json")
    args=parser.parse_args()
    p=export_snapshot(args.database,args.output)
    print(json.dumps({"output":str(Path(args.output).resolve()),
      "database_sha256":p["source_database"]["database_sha256"],
      "wal_sha256":p["source_database"]["wal_sha256"],
      "integrity_check":p["integrity_check"],
      "foreign_key_violation_count":p["foreign_key_violation_count"],
      "missing_product_ids":p["missing_product_ids"],
      "table_row_counts":p["table_row_counts"]},ensure_ascii=False,indent=2))
    return 0 if not p["missing_product_ids"] else 2

if __name__=="__main__": raise SystemExit(main())
