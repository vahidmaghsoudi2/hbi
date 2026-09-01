-- HBI Accounting PHASE 02 — additive schema (SQLite)
-- Does NOT drop legacy toman columns. Does NOT rewrite money values.
PRAGMA foreign_keys=OFF;
BEGIN;

CREATE TABLE IF NOT EXISTS Category (
  category_id VARCHAR PRIMARY KEY,
  name_fa VARCHAR NOT NULL,
  name_en VARCHAR,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO Category (category_id, name_fa, name_en, is_active, sort_order) VALUES
 ('BOOST', 'بوست', 'Boost', 1, 1),
 ('HAIR', 'مو', 'Hair', 1, 2),
 ('BEAUTY', 'زیبایی', 'Beauty', 1, 3),
 ('TOOLS', 'ابزار', 'Tools', 1, 4),
 ('PERFUME', 'ادکلن', 'Perfume', 1, 5),
 ('OTHER', 'سایر', 'Other', 1, 99);

CREATE TABLE IF NOT EXISTS StockMovement (
  movement_id VARCHAR PRIMARY KEY,
  product_id VARCHAR NOT NULL,
  inventory_id VARCHAR,
  movement_type VARCHAR NOT NULL,
  quantity_delta INTEGER NOT NULL,
  quantity_after INTEGER,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman FLOAT,
  reference_type VARCHAR,
  reference_id VARCHAR,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(product_id) REFERENCES Product(product_id)
);

CREATE TABLE IF NOT EXISTS Payment (
  payment_id VARCHAR PRIMARY KEY,
  sale_id VARCHAR NOT NULL,
  method VARCHAR NOT NULL,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman INTEGER,
  paid_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sale_id) REFERENCES Sale(sale_id)
);

CREATE TABLE IF NOT EXISTS SaleReturn (
  return_id VARCHAR PRIMARY KEY,
  sale_id VARCHAR NOT NULL,
  product_id VARCHAR NOT NULL,
  quantity INTEGER NOT NULL,
  amount_usd FLOAT,
  fx_rate_usd_to_irr FLOAT,
  amount_irr FLOAT,
  amount_toman INTEGER,
  reason VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sale_id) REFERENCES Sale(sale_id),
  FOREIGN KEY(product_id) REFERENCES Product(product_id)
);

CREATE TABLE IF NOT EXISTS OperationalFxRate (
  rate_id VARCHAR PRIMARY KEY,
  fx_rate_usd_to_irr FLOAT NOT NULL,
  effective_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  note VARCHAR,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
PRAGMA foreign_keys=ON;
