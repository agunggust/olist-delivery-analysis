SELECT
    SUBSTR(delivered_date, 1, 7) AS delivery_month,
    destination_state,
    COUNT(*) AS delivered_orders,
    SUM(is_late) AS late_orders,
    100.0 * SUM(is_late) / COUNT(*) AS late_pct
FROM delivery_orders
GROUP BY delivery_month, destination_state
ORDER BY delivery_month, destination_state;
