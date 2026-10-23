{{ config(materialized='table') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

dim_seller AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['seller_id']) }} AS seller_key,
        CAST(seller_id AS INTEGER) AS seller_id,
        CAST(seller_city AS TEXT) AS seller_city,
        CAST(seller_country AS TEXT) AS seller_country,
        CAST(is_best_seller AS BOOLEAN) AS is_best_seller,
        CAST(is_power_seller AS BOOLEAN) AS is_power_seller,
        CAST(power_seller_status_title AS TEXT) AS seller_id,
    FROM silver
)

SELECT *
FROM dim_seller