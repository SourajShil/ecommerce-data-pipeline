SELECT
    o.order_id,
    o.customer_id,
    o.ordered_at,
    o.status,
    c.full_name     AS customer_name,
    c.city,
    c.country,
    SUM(oi.line_total) AS order_revenue,
    SUM(oi.quantity)   AS total_items
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('stg_customers') }} c USING (customer_id)
JOIN {{ ref('stg_order_items') }} oi USING (order_id)
GROUP BY 1, 2, 3, 4, 5, 6, 7
