{{ config(materialized='table') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

dim_seller AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['seller_id']) }} AS seller_key,
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
    FROM silver
)

SELECT *
FROM dim_seller