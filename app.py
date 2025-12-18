from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
DB_NAME = "db.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = get_db_connection()

    cryptos = conn.execute(
        "SELECT * FROM cryptocurrencies ORDER BY market_cap DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) as count FROM cryptocurrencies"
    ).fetchone()["count"]

    pipeline_status = conn.execute(
        "SELECT status, run_time FROM pipeline_runs ORDER BY run_time DESC LIMIT 1"
    ).fetchone()

    conn.close()

    return render_template(
        "index.html",
        cryptos=cryptos,
        total=total,
        pipeline_status=pipeline_status
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

