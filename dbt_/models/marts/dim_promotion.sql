{{ config(
    materialized='external',
    location='s3://mlbvncs-valuemetrics-dev/gold/mercadolivre/celulares-e-telefones/dim_promotion.parquet',
    format='parquet'
) }}

WITH promotion_stg AS (
    SELECT *
    FROM {{ ref('stg_promotion') }}
),

SELECT
    {{ dbt_utils.generate_surrogate_key(['highlight']) }} AS promotion_key,
    *
FROM promotion_stg