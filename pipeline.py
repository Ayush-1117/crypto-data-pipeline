import requests
import sqlite3
import logging
from datetime import datetime

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_NAME = "db.sqlite"
USD_TO_INR = 83.0

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()

# ---------------- FETCH DATA ----------------
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# ---------------- TRANSFORM DATA ----------------
def transform_data(raw_data):
    transformed = []

    for coin in raw_data:
        transformed.append({
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"].upper(),
            "price_usd": coin["current_price"],
            "price_inr": round(coin["current_price"] * USD_TO_INR, 2),
            "market_cap": coin["market_cap"],
            "price_change_24h": coin["price_change_percentage_24h"]
        })

    return transformed

# ---------------- STORE DATA ----------------
def store_data(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for coin in data:
        cursor.execute("""
            INSERT INTO cryptocurrencies VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                price_usd=excluded.price_usd,
                price_inr=excluded.price_inr,
                market_cap=excluded.market_cap,
                price_change_24h=excluded.price_change_24h,
                last_updated=excluded.last_updated
        """, (
            coin["id"],
            coin["name"],
            coin["symbol"],
            coin["price_usd"],
            coin["price_inr"],
            coin["market_cap"],
            coin["price_change_24h"],
            datetime.utcnow()
        ))

    conn.commit()
    conn.close()

# ---------------- PIPELINE RUN LOG ----------------
def log_pipeline_run(status, message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pipeline_runs VALUES (?, ?, ?)
    """, (datetime.utcnow(), status, message))

    conn.commit()
    conn.close()

# ---------------- MAIN ----------------
def main():
    init_db()
    try:
        raw = fetch_crypto_data()
        transformed = transform_data(raw)
        store_data(transformed)
        log_pipeline_run("SUCCESS", "Pipeline ran successfully")
        print("✅ Pipeline completed successfully")
    except Exception as e:
        logging.error(str(e))
        log_pipeline_run("FAILED", str(e))
        print("❌ Pipeline failed")

# if __name__ == "__main__":
#     main()
def run_pipeline():
    main()

if __name__ == "__main__":
    run_pipeline()

