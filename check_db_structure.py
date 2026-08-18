from app.database import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()

print("=== Database Structure ===")
print("=" * 60)

# لیست همه جداول
inspector = inspect(db.get_bind())
tables = inspector.get_table_names()

print(f"Total tables: {len(tables)}")
print()
print("ALL TABLES:")
for t in sorted(tables):
    print(f"  - {t}")

print()
print("=" * 60)
print("Searching for product-related tables...")
print("=" * 60)

product_tables = [t for t in tables if 'product' in t.lower()]
if product_tables:
    print(f"Found {len(product_tables)} product tables:")
    for t in product_tables:
        print(f"\n  TABLE: {t}")
        cols = inspector.get_columns(t)
        print(f"  Columns ({len(cols)}):")
        for col in cols[:15]:  # فقط ۱۵ ستون اول
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"    - {col['name']:30s} ({nullable})")
        if len(cols) > 15:
            print(f"    ... and {len(cols) - 15} more columns")
else:
    print("NO product tables found!")

db.close()
