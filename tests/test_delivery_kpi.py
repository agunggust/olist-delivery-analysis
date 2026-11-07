"""Check the delivery KPI without downloading the Olist dataset."""
import sqlite3
import unittest

from build import run_sql


class DeliveryKpiTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript("""
            CREATE TABLE customers (customer_id TEXT PRIMARY KEY, customer_state TEXT);
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY, customer_id TEXT, order_status TEXT,
                delivered_at TEXT, estimated_at TEXT
            );
            INSERT INTO customers VALUES ('customer', 'SP');
        """)
        run_sql(self.db, "01_delivery_orders.sql")

    def test_calendar_date_defines_lateness(self):
        self.db.executescript("""
            INSERT INTO orders VALUES
                ('early', 'customer', 'delivered', '2018-01-01', '2018-01-02'),
                ('same_day', 'customer', 'delivered', '2018-01-02 17:00:00', '2018-01-02'),
                ('late', 'customer', 'delivered', '2018-01-03', '2018-01-02');
        """)
        orders = self.db.execute("""
            SELECT order_id, days_vs_estimate, is_late
            FROM delivery_orders ORDER BY order_id
        """).fetchall()
        self.assertEqual(orders, [("early", -1, 0), ("late", 1, 1), ("same_day", 0, 0)])

    def test_only_delivered_orders_with_both_dates_are_eligible(self):
        self.db.executescript("""
            INSERT INTO orders VALUES
                ('valid', 'customer', 'delivered', '2018-01-03', '2018-01-02'),
                ('no_actual', 'customer', 'delivered', '', '2018-01-02'),
                ('no_estimate', 'customer', 'delivered', '2018-01-03', NULL),
                ('canceled', 'customer', 'canceled', '2018-01-03', '2018-01-02');
        """)
        self.assertEqual(run_sql(self.db, "02_state_priority.sql").fetchall(),
                         [("SP", 1, 1, 100.0)])
        self.assertEqual(run_sql(self.db, "03_monthly_trend.sql").fetchall(),
                         [("2018-01", "SP", 1, 1, 100.0)])


if __name__ == "__main__":
    unittest.main()
