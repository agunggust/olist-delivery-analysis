CREATE VIEW delivery_orders AS
SELECT
    o.order_id,
    c.customer_state AS destination_state,
    DATE(o.delivered_at) AS delivered_date,
    DATE(o.estimated_at) AS estimated_date,
    CAST(JULIANDAY(DATE(o.delivered_at)) -
         JULIANDAY(DATE(o.estimated_at)) AS INTEGER) AS days_vs_estimate,
    CASE WHEN DATE(o.delivered_at) > DATE(o.estimated_at)
         THEN 1 ELSE 0 END AS is_late
FROM orders AS o
JOIN customers AS c USING (customer_id)
WHERE o.order_status = 'delivered'
  AND DATE(o.delivered_at) IS NOT NULL
  AND DATE(o.estimated_at) IS NOT NULL;
