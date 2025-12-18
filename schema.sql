CREATE TABLE IF NOT EXISTS cryptocurrencies (
    id TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    price_usd REAL,
    price_inr REAL,
    market_cap REAL,
    price_change_24h REAL,
    last_updated DATETIME
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_time DATETIME,
    status TEXT,
    message TEXT
);
