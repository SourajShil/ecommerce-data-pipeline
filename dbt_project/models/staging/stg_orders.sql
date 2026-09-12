SELECT
    order_id,
    customer_id,
    ordered_at,
    status
FROM {{ source('raw', 'raw_orders') }}
WHERE status != 'cancelled'
