{{ config(materialized='table') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

dim_product AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['url', 'sku']) }} AS product_key,
        CAST(url AS TEXT) AS url,
        CAST(sku AS TEXT) AS sku,
        CAST(ean AS TEXT) AS ean,
        CAST(image_url AS TEXT) AS image_url,
        CAST(category_id AS TEXT) AS category_id,
        CAST(domain_id AS TEXT) AS domain_id,
        CAST(name AS TEXT) AS name,
        CAST(condition AS TEXT) AS condition
    FROM silver
)

SELECT *
FROM dim_product