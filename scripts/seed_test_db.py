import sqlite3, os, tempfile
from pathlib import Path

def main():
    db_path = Path(tempfile.mkdtemp(prefix="hbi_seed_")) / "hbi_test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute('''CREATE TABLE IF NOT EXISTS Product (
        product_id TEXT PRIMARY KEY, brand TEXT NOT NULL, product_name TEXT NOT NULL,
        variant TEXT, identity_status TEXT, identity_confidence REAL, qa_verdict TEXT, qa_notes TEXT)''')
    conn.execute('''INSERT INTO Product VALUES 
        ('TEST-001', 'TEST', 'Test Product 001', 'E2E', 'VERIFIED', 1.0, 'VALID', 'Fixture'),
        ('TEST-002', 'TEST', 'Test Product 002', 'E2E', 'VERIFIED', 1.0, 'VALID', 'Fixture')''')
    conn.commit()
    conn.close()
    print(f"✅ Seed DB created at: {db_path}")

if __name__ == "__main__": main()