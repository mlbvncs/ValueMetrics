{{ config(materialized='table') }}

WITH silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

dim_store AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['store']) }} AS store_key,
        'Mercado Livre' AS store
    FROM silver
)

SELECT *
FROM dim_store