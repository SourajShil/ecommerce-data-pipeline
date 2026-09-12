SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity)                   AS units_sold,
    ROUND(SUM(oi.line_total), 2)       AS total_revenue,
    RANK() OVER (
        PARTITION BY p.category
        ORDER BY SUM(oi.line_total) DESC
    )                                  AS rank_in_category
FROM {{ ref('stg_order_items') }} oi
JOIN {{ ref('stg_products') }} p USING (product_id)
JOIN {{ ref('stg_orders') }} o USING (order_id)
GROUP BY 1, 2, 3
