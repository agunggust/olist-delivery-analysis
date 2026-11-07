-- Compare the same calendar months in two non-overlapping years.
WITH state_totals AS (
    SELECT SUBSTR(delivered_date, 1, 4) AS delivery_year,
           destination_state,
           COUNT(*) AS delivered_orders,
           SUM(is_late) AS late_orders
    FROM delivery_orders
    WHERE (delivered_date >= '2017-01-01' AND delivered_date < '2017-09-01')
       OR (delivered_date >= '2018-01-01' AND delivered_date < '2018-09-01')
    GROUP BY delivery_year, destination_state
    HAVING COUNT(*) >= 500
),
ranked AS (
    SELECT *, 100.0 * late_orders / delivered_orders AS late_pct,
           ROW_NUMBER() OVER (
               PARTITION BY delivery_year ORDER BY late_orders DESC,
                   delivered_orders DESC, destination_state
           ) AS priority
    FROM state_totals
)
SELECT * FROM ranked WHERE priority <= 3 ORDER BY delivery_year, priority;
