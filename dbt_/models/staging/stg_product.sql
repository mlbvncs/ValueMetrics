{{ config(materialized='view') }}

WITH product_silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

stg_product AS (
    SELECT
        COALESCE(sku, 'Sem informação') AS sku,
        COALESCE(ean, 'Sem informação') AS ean,
        COALESCE(image_url, 'Sem informação') AS image_url,
        COALESCE(category_id, 'Sem informação') AS category_id,
        COALESCE(domain_id, 'Sem informação') AS domain_id,
        COALESCE(name, 'Sem informação') AS name,
        COALESCE(condition, 'Sem informação') AS condition
    FROM product_silver
),

product_deduplicate AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY sku, ean, image_url, category_id, domain_id, name, condition
        ) AS product_rank
    FROM stg_product
)

SELECT 
    *
FROM product_deduplicate
WHERE product_rank = 1
