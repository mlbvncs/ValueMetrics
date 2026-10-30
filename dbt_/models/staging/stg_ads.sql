{{ config(materialized='view') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

SELECT
    COALESCE(sku, 'Sem informação') AS sku,
    COALESCE(ean, 'Sem informação') AS ean,
    COALESCE(image_url, 'Sem informação') AS image_url,
    COALESCE(category_id, 'Sem informação') AS category_id,
    COALESCE(domain_id, 'Sem informação') AS domain_id,
    COALESCE(name, 'Sem informação') AS name,
    COALESCE(condition, 'Sem informação') AS condition,
    COALESCE(seller_id, 'Sem informação') AS seller_id,
    COALESCE(seller_name, 'Sem informação') AS seller_name,
    COALESCE(seller_city, 'Sem informação') AS seller_city,
    COALESCE(seller_state, 'Sem informação') AS seller_state,
    COALESCE(seller_country, 'Sem informação') AS seller_country,
    CASE
        WHEN is_best_seller IS NULL THEN 'Sem informação'
        WHEN is_best_seller THEN 'Verdadeiro'
        ELSE 'Falso'
    END AS is_best_seller,
    CASE
        WHEN is_power_seller IS NULL THEN 'Sem informação'
        WHEN is_power_seller THEN 'Verdadeiro'
        ELSE 'Falso'
    END AS is_power_seller,
    COALESCE(power_seller_status_title, 'Sem informação') AS power_seller_status_title,
    COALESCE(highlight, 'Sem destaque') AS highlight,
    COALESCE(currency, 'Sem informação') AS currency,
    COALESCE(currency_raw, 'Sem informação') AS currency_raw,
    price,
    rating,
    review_count,
    url,
    COALESCE(extracted_at, 'Sem informação') AS extracted_at
FROM silver