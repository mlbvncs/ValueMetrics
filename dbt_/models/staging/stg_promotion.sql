{{ config(materialized='view') }}

WITH promotion_silver AS (
    SELECT *
    FROM {{ source('silver_S3', 'silver_data') }}
),

stg_promotion AS (
    SELECT
        COALESCE(highlight, 'Sem destaque') AS highlight
    FROM promotion_silver
),

promotion_deduplicate AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY highlight
        ) AS promotion_rank
    FROM stg_promotion
)

SELECT
    *
FROM promotion_deduplicate
WHERE promotion_rank = 1