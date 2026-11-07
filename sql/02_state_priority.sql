SELECT
    destination_state,
    COUNT(*) AS delivered_orders,
    SUM(is_late) AS late_orders,
    100.0 * SUM(is_late) / COUNT(*) AS late_pct
FROM delivery_orders
GROUP BY destination_state
ORDER BY late_orders DESC, delivered_orders DESC, destination_state;
