{{ config(materialized='table') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

dim_product AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['url', 'sku']) }} AS product_key,
        url,
        sku,
        COALESCE(ean, 'Sem informação') AS ean,
        COALESCE(image_url, 'Sem informação') AS image_url,
        COALESCE(category_id, 'Sem informação') AS category_id,
        COALESCE(domain_id, 'Sem informação') AS domain_id,
        COALESCE(name, 'Sem informação') AS name,
        COALESCE(condition, 'Sem informação') AS condition
    FROM silver
)

SELECT *
FROM dim_product