SELECT
    customer_id,
    full_name,
    email,
    city,
    country,
    created_at
FROM {{ source('raw', 'raw_customers') }}
