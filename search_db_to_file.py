from app.database import SessionLocal
from sqlalchemy import text
from datetime import datetime

db = SessionLocal()
rpt = []

def log(s=""):
    rpt.append(str(s))

log("# Database Structure Search Report")
log(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("")

# لیست همه جداول
result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
tables = [r[0] for r in result]

log(f"## Total Tables: {len(tables)}")
log("")
log("### All Tables:")
for t in sorted(tables):
    log(f"- {t}")
log("")

products = [
    'ISDIN-FUSION-WATER-MAGIC-50',
    'ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50'
]

for pid in products:
    log(f"## PRODUCT: {pid}")
    log("")
    
    found_in_tables = []
    
    for table in tables:
        try:
            cols_result = db.execute(text(f"PRAGMA table_info({table})")).fetchall()
            col_names = [c[1] for c in cols_result]
            
            if 'product_id' in col_names:
                query = f"SELECT * FROM {table} WHERE product_id = '{pid}'"
                rows = db.execute(text(query)).fetchall()
                
                if rows:
                    found_in_tables.append(table)
                    log(f"### Found in: {table}")
                    log(f"**Row count:** {len(rows)}")
                    log("")
                    log("**Columns:**")
                    log("")
                    
                    for row in rows[:1]:  # فقط اولین رکورد
                        for j, col in enumerate(col_names):
                            val = row[j]
                            if val is not None:
                                display = str(val)[:80]
                                log(f"- ✓ {col}: {display}")
                            else:
                                log(f"- ❓ {col}: NULL")
                    log("")
        except Exception as e:
            pass
    
    if not found_in_tables:
        log(f"**Result:** NOT FOUND in any table")
        log("")
    else:
        log(f"**Summary:** Found in {len(found_in_tables)} table(s): {', '.join(found_in_tables)}")
        log("")

db.close()

with open("db_search_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rpt))

print("Report saved to: db_search_report.txt")
print(f"Total tables: {len(tables)}")
print("Next: notepad db_search_report.txt")
