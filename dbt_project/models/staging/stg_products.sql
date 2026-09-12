SELECT
    product_id,
    product_name,
    category,
    unit_price,
    created_at
FROM {{ source('raw', 'raw_products') }}
