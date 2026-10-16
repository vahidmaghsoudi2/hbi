"""Create isolated, disposable DB fixtures for the Playwright pilot proof."""
from pathlib import Path
import os
import sys
import tempfile

from sqlalchemy.engine import make_url

# Running a script from scripts/ sets sys.path[0] to that directory, not the repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("HBI_ENV", "development")
db_url = os.environ.get("DATABASE_URL")
if not db_url or not db_url.startswith("sqlite:///"):
    raise SystemExit("Refusing browser setup without an explicit disposable SQLite DATABASE_URL")

if os.environ.get("HBI_PILOT_FIXTURE_MODE") != "browser-fixture":
    raise SystemExit("Refusing fixture seeding unless HBI_PILOT_FIXTURE_MODE=browser-fixture")

try:
    database_name = make_url(db_url).database
except Exception as exc:
    raise SystemExit(f"Refusing invalid DATABASE_URL: {exc}") from exc

if not database_name or database_name == ":memory:":
    raise SystemExit("Refusing browser setup: a file-backed disposable SQLite DB is required")

db_path = Path(database_name)
if not db_path.is_absolute():
    raise SystemExit("Refusing browser setup: DATABASE_URL must resolve to an absolute file path")

temp_root = Path(tempfile.gettempdir()).resolve()
pilot_root = temp_root / "hbi-g8-pilot"
if pilot_root.is_symlink():
    raise SystemExit(f"Refusing browser setup: pilot root cannot be a symlink: {pilot_root}")
pilot_root.mkdir(parents=True, exist_ok=True)

resolved_db_path = db_path.resolve(strict=False)
if resolved_db_path.parent != pilot_root.resolve():
    raise SystemExit(
        "Refusing browser setup: SQLite file must be directly inside the dedicated "
        f"temporary pilot directory {pilot_root}; got {resolved_db_path}"
    )
if resolved_db_path.name not in {"pilot-browser-proof.sqlite", "pilot.db"}:
    raise SystemExit("Refusing browser setup: unexpected disposable database filename")
if db_path.is_symlink():
    raise SystemExit("Refusing browser setup: database target cannot be a symlink")
if db_path.exists() and db_path.stat().st_size > 0:
    raise SystemExit(
        f"Refusing browser setup: database already exists and is non-empty: {db_path}"
    )

from app.database import init_db, SessionLocal
from scripts.seed_products_from_records import seed
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge

init_db()
db = SessionLocal()
try:
    seed(db)
    product = db.query(Product).filter_by(product_id="ISDIN-FOTOUTRA100-50ML").one()
    product.status = "ACTIVE"
    product.identity_status = "VERIFIED"
    product.qa_verdict = "VALID"
    inv = db.query(Inventory).filter_by(product_id=product.product_id).first()
    if inv is None:
        inv = Inventory(
            inventory_id=f"INV-{product.product_id}",
            product_id=product.product_id,
            quantity_available=5,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="AVAILABLE",
            sale_price_usd=20.0,
            sale_price_toman=2_000_000,
        )
        db.add(inv)
    else:
        inv.quantity_available = max(int(inv.quantity_available or 0), 5)
        inv.quantity_reserved = int(inv.quantity_reserved or 0)
        if inv.sale_price_usd is None:
            inv.sale_price_usd = 20.0
        if inv.sale_price_toman is None:
            inv.sale_price_toman = 2_000_000
        inv.stock_status = "AVAILABLE"
    pk = db.query(ProductKnowledge).filter_by(product_id=product.product_id).one()
    pk.known_use_cases = "sun protection"
    if db.get(Evidence, "EV-PILOT-BROWSER-APPROVED-001") is None:
        db.add(Evidence(
            evidence_id="EV-PILOT-BROWSER-APPROVED-001",
            product_id=product.product_id,
            source_type="INDEPENDENT",
            source_reference="TEST-PILOT-BROWSER-FIXTURE",
            claim="approved test support for sunscreen use case",
            claim_type="FACT",
            evidence_status="SUPPORTED",
            qa_status="APPROVED",
            conflict_status="NONE",
        ))
    if db.get(Customer, "CUST-PILOT-1") is None:
        db.add(Customer(customer_id="CUST-PILOT-1", name="Browser Pilot User"))
    db.commit()
finally:
    db.close()
