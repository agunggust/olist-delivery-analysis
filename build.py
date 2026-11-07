"""Build the SQLite analysis and standalone dashboard from the Olist ZIP."""
import argparse
import csv
import io
import json
import sqlite3
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent


def source_rows(archive, filename, columns):
    with archive.open(filename) as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                yield tuple(row[column] for column in columns)


def load_source(db, archive):
    db.executescript("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY NOT NULL,
            customer_state TEXT NOT NULL CHECK (length(customer_state) = 2)
        );
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY NOT NULL,
            customer_id TEXT NOT NULL REFERENCES customers (customer_id),
            order_status TEXT NOT NULL,
            delivered_at TEXT,
            estimated_at TEXT
        );
    """)
    db.executemany(
        "INSERT INTO customers VALUES (?, ?)",
        source_rows(archive, "olist_customers_dataset.csv", (
            "customer_id", "customer_state",
        )),
    )
    db.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
        source_rows(archive, "olist_orders_dataset.csv", (
            "order_id", "customer_id", "order_status",
            "order_delivered_customer_date", "order_estimated_delivery_date",
        )),
    )


def run_sql(db, filename):
    return db.execute((ROOT / "sql" / filename).read_text(encoding="ascii"))


def build(zip_path):
    with sqlite3.connect(":memory:") as db, ZipFile(zip_path) as archive:
        db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = sqlite3.Row
        load_source(db, archive)
        run_sql(db, "01_delivery_orders.sql")
        order_count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        eligible_count = db.execute("""
            SELECT COUNT(*) FROM orders
            WHERE order_status = 'delivered'
              AND DATE(delivered_at) IS NOT NULL
              AND DATE(estimated_at) IS NOT NULL
        """).fetchone()[0]
        totals = db.execute("""
            SELECT COUNT(*) AS delivered_orders, SUM(is_late) AS late_orders,
                   COUNT(DISTINCT order_id) AS unique_orders,
                   MIN(delivered_date) AS first_delivery,
                   MAX(delivered_date) AS last_delivery
            FROM delivery_orders
        """).fetchone()
        if not eligible_count or totals["delivered_orders"] != eligible_count or (
            totals["unique_orders"] != eligible_count
        ):
            raise ValueError("Expected exactly one row per eligible order.")

        states = [dict(row) for row in run_sql(db, "02_state_priority.sql")]
        monthly = [dict(row) for row in run_sql(db, "03_monthly_trend.sql")]
        for rows in (states, monthly):
            for field in ("delivered_orders", "late_orders"):
                if sum(row[field] for row in rows) != totals[field]:
                    raise ValueError(f"Aggregate does not reconcile for {field}.")

        db.commit()
        with sqlite3.connect(ROOT / "delivery.sqlite") as output:
            db.backup(output)

    data = {"source_orders": order_count, "totals": dict(totals),
            "states": states, "monthly": monthly}
    template = (ROOT / "dashboard.template.html").read_text(encoding="utf-8")
    payload = json.dumps(data).replace("<", "\\u003c")
    (ROOT / "dashboard.html").write_text(
        template.replace("/* DASHBOARD_DATA */", payload), encoding="utf-8"
    )
    print(json.dumps({
        "source_orders": order_count,
        "totals": dict(totals),
        "top_states": states[:5],
        "priority_months": [
            row for row in monthly
            if row["destination_state"] == states[0]["destination_state"]
        ],
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", nargs="?", type=Path, default=ROOT / "olist-source.zip")
    build(parser.parse_args().zip)
