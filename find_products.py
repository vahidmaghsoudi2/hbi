from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

products = [
    'ISDIN-FUSION-WATER-MAGIC-50',
    'ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50'
]

print("=== Real Product Data Search ===")
print("=" * 70)

# لیست همه جداول
result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
tables = [r[0] for r in result]

print(f"Total tables in database: {len(tables)}")
print()

for pid in products:
    print(f"\n{'='*70}")
    print(f"PRODUCT: {pid}")
    print('='*70)
    
    # جستجو در هر جدول
    for table in tables:
        try:
            # بررسی آیا این جدول ستون product_id دارد
            cols_result = db.execute(text(f"PRAGMA table_info({table})")).fetchall()
            col_names = [c[1] for c in cols_result]
            
            if 'product_id' in col_names:
                # Query برای این product
                query = f"SELECT * FROM {table} WHERE product_id = '{pid}'"
                rows = db.execute(text(query)).fetchall()
                
                if rows:
                    print(f"\n  TABLE: {table} ({len(rows)} row(s))")
                    print(f"  Columns: {', '.join(col_names[:10])}")
                    if len(col_names) > 10:
                        print(f"           ... and {len(col_names) - 10} more")
                    
                    # نمایش داده‌ها
                    for i, row in enumerate(rows[:2]):  # فقط ۲ رکورد اول
                        print(f"\n  Row {i+1}:")
                        for j, col in enumerate(col_names):
                            val = row[j]
                            if val is not None:
                                display = str(val)[:60]
                                print(f"    ✓ {col:30s} = {display}")
                            else:
                                print(f"    ❓ {col:30s} = NULL")
        except Exception as e:
            pass  # Skip tables that cause errors

db.close()

print("\n" + "="*70)
print("Search complete")
print("="*70)
