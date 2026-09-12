SELECT
    item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS line_total
FROM {{ source('raw', 'raw_order_items') }}
