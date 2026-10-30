{{ config(
    materialized='external',
    location='s3://mlbvncs-valuemetrics-dev/gold/mercadolivre/celulares-e-telefones/fct_ads.parquet',
    format='parquet'
) }}

WITH silver AS (
    SELECT *
    FROM {{ ref('stg_ads') }}
),

dim_currency as (
    SELECT *
    FROM {{ ref('dim_currency') }}
),

dim_product as (
    SELECT *
    FROM {{ ref('dim_product') }}
),

dim_promotion as (
    SELECT *
    FROM {{ ref('dim_promotion') }}
),

dim_seller as (
    SELECT *
    FROM {{ ref('dim_seller') }}
)

SELECT
    dc.currency_key AS currency_key,
    dprod.product_key AS product_key,
    dprom.promotion_key AS promotion_key,
    ds.seller_key AS seller_key,
    s.price AS price,
    s.rating AS rating,
    s.review_count AS review_count,
    s.url AS url,
    s.extracted_at AS extracted_at
FROM silver s
LEFT JOIN dim_currency dc
    ON s.currency = dc.currency
    AND s.currency_raw = dc.currency_raw
LEFT JOIN dim_product dprod
    ON s.sku = dprod.sku
    AND s.ean = dprod.ean
    AND s.image_url = dprod.image_url
    AND s.category_id = dprod.category_id
    AND s.domain_id = dprod.domain_id
    AND s.name = dprod.name
    AND s.condition = dprod.condition
LEFT JOIN dim_promotion dprom
    ON s.highlight = dprom.highlight
LEFT JOIN dim_seller ds
    ON s.seller_id = ds.seller_id
    AND s.seller_name = ds.seller_name
    AND s.seller_city = ds.seller_city
    AND s.seller_state = ds.seller_state
    AND s.seller_country = ds.seller_country
    AND s.is_best_seller = ds.is_best_seller
    AND s.is_power_seller = ds.is_power_seller
    AND s.power_seller_status_title = ds.power_seller_status_title