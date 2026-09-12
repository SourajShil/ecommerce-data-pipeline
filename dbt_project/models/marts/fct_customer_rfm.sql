WITH rfm_base AS (
    SELECT
        customer_id,
        customer_name,
        city,
        country,
        MAX(ordered_at)                        AS last_order_date,
        COUNT(DISTINCT order_id)               AS frequency,
        ROUND(SUM(order_revenue), 2)           AS monetary,
        CURRENT_DATE - MAX(ordered_at)::date   AS recency_days
    FROM {{ ref('int_orders_enriched') }}
    GROUP BY 1, 2, 3, 4
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC)    AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC)     AS m_score
    FROM rfm_base
)
SELECT
    *,
    ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_avg,
    CASE
        WHEN (r_score + f_score + m_score) >= 12 THEN 'Champion'
        WHEN (r_score + f_score + m_score) >= 9  THEN 'Loyal'
        WHEN (r_score + f_score + m_score) >= 6  THEN 'At Risk'
        ELSE 'Lost'
    END AS customer_segment
FROM rfm_scored
