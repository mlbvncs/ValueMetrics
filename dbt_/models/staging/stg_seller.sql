{{ config(materialized='view') }}

WITH seller_silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

stg_seller AS (
    SELECT
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
        COALESCE(power_seller_status_title, 'Sem informação') AS power_seller_status_title
    FROM seller_silver
),

seller_deduplicate AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY seller_id, seller_name, seller_city, seller_state, seller_country, is_best_seller, is_power_seller, power_seller_status_title
        ) AS seller_rank
    FROM stg_seller
)

SELECT 
    *
FROM seller_deduplicate
WHERE seller_rank = 1