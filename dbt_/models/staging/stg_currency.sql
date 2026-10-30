{{ config(materialized='view') }}

WITH currency_silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

stg_currency AS (
    SELECT
        COALESCE(currency, 'Sem informação') AS currency,
        COALESCE(currency_raw, 'Sem informação') AS currency_raw,
    FROM currency_silver
),

currency_deduplicate AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY currency, currency_raw
        ) AS currency_rank
    FROM stg_currency
)

SELECT 
    *
FROM currency_deduplicate
WHERE currency_rank = 1