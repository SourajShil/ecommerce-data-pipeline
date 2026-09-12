SELECT
    DATE_TRUNC('day', ordered_at)::date AS sale_date,
    COUNT(DISTINCT order_id)            AS total_orders,
    COUNT(DISTINCT customer_id)         AS unique_customers,
    SUM(order_revenue)                  AS total_revenue,
    ROUND(AVG(order_revenue), 2)        AS avg_order_value
FROM {{ ref('int_orders_enriched') }}
GROUP BY 1
ORDER BY 1
